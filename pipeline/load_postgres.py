from __future__ import annotations
import os
import pandas as pd
from sqlalchemy import create_engine, text

DDL = """
CREATE TABLE IF NOT EXISTS dim_participant (
  participant_id BIGINT PRIMARY KEY,
  age INTEGER, gender TEXT, height_cm DOUBLE PRECISION, weight_kg DOUBLE PRECISION,
  bmi DOUBLE PRECISION, smoking_status TEXT
);
CREATE TABLE IF NOT EXISTS dim_workout_type (
  activity_type TEXT PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS dim_date (
  date_key DATE PRIMARY KEY,
  year INTEGER, month INTEGER, day INTEGER, weekday TEXT
);
CREATE TABLE IF NOT EXISTS fact_workout_activity (
  participant_id BIGINT NOT NULL,
  activity_date DATE NOT NULL,
  activity_type TEXT NOT NULL,
  duration_minutes INTEGER,
  intensity TEXT,
  calories_burned DOUBLE PRECISION,
  avg_heart_rate DOUBLE PRECISION,
  hours_sleep DOUBLE PRECISION,
  stress_level INTEGER,
  daily_steps INTEGER,
  hydration_level DOUBLE PRECISION,
  fitness_level DOUBLE PRECISION,
  source_hash TEXT,
  PRIMARY KEY (participant_id, activity_date)
);
CREATE INDEX IF NOT EXISTS idx_fact_activity_date ON fact_workout_activity(activity_date);
CREATE INDEX IF NOT EXISTS idx_fact_activity_type ON fact_workout_activity(activity_type);
CREATE TABLE IF NOT EXISTS daily_activity_aggregate (
  activity_date DATE NOT NULL,
  activity_type TEXT NOT NULL,
  workout_count BIGINT,
  active_participants BIGINT,
  avg_duration DOUBLE PRECISION,
  avg_calories DOUBLE PRECISION,
  PRIMARY KEY (activity_date, activity_type)
);
CREATE TABLE IF NOT EXISTS participant_graph_metrics (
  participant_id BIGINT PRIMARY KEY,
  degree_centrality DOUBLE PRECISION,
  betweenness_centrality DOUBLE PRECISION,
  community_id INTEGER
);
"""

def load_warehouse(df: pd.DataFrame, profiles: pd.DataFrame, graph_metrics: pd.DataFrame):
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not set; skipping PostgreSQL load.")
        return
    engine = create_engine(url, pool_pre_ping=True)
    with engine.begin() as conn:
        for statement in DDL.split(";"):
            if statement.strip():
                conn.execute(text(statement))
    # Dimensions are refreshed from the current snapshot.
    participants = df.groupby("participant_id").agg(
        age=("age","first"), gender=("gender","first"), height_cm=("height_cm","first"),
        weight_kg=("weight_kg","first"), bmi=("bmi","first"), smoking_status=("smoking_status","first")
    ).reset_index()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM dim_participant"))
        conn.execute(text("DELETE FROM dim_workout_type"))
    participants.to_sql("dim_participant", engine, if_exists="append", index=False, chunksize=1000, method="multi")
    pd.DataFrame({"activity_type": sorted(df["activity_type"].dropna().unique())}).to_sql(
        "dim_workout_type", engine, if_exists="append", index=False, method="multi")
    dates = pd.to_datetime(df["date"])
    date_dim = pd.DataFrame({"date_key": dates.dt.date, "year": dates.dt.year,
        "month": dates.dt.month, "day": dates.dt.day, "weekday": dates.dt.day_name()}).drop_duplicates()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM dim_date"))
    date_dim.to_sql("dim_date", engine, if_exists="append", index=False, chunksize=1000, method="multi")
    fact = df[["participant_id","date","activity_type","duration_minutes","intensity",
               "calories_burned","avg_heart_rate","hours_sleep","stress_level","daily_steps",
               "hydration_level","fitness_level"]].copy().rename(columns={"date":"activity_date"})
    fact["source_hash"] = fact.astype(str).agg("|".join, axis=1).map(
        lambda x: __import__("hashlib").sha256(x.encode()).hexdigest())
    # Idempotent staging + upsert.
    fact.to_sql("stg_workout_activity", engine, if_exists="replace", index=False, chunksize=5000, method="multi")
    with engine.begin() as conn:
        conn.execute(text("""
          INSERT INTO fact_workout_activity
          SELECT participant_id, activity_date::date, activity_type, duration_minutes, intensity,
                 calories_burned, avg_heart_rate, hours_sleep, stress_level, daily_steps,
                 hydration_level, fitness_level, source_hash
          FROM stg_workout_activity
          ON CONFLICT (participant_id, activity_date) DO UPDATE SET
            activity_type=EXCLUDED.activity_type,
            duration_minutes=EXCLUDED.duration_minutes,
            intensity=EXCLUDED.intensity,
            calories_burned=EXCLUDED.calories_burned,
            avg_heart_rate=EXCLUDED.avg_heart_rate,
            hours_sleep=EXCLUDED.hours_sleep,
            stress_level=EXCLUDED.stress_level,
            daily_steps=EXCLUDED.daily_steps,
            hydration_level=EXCLUDED.hydration_level,
            fitness_level=EXCLUDED.fitness_level,
            source_hash=EXCLUDED.source_hash
        """))
        conn.execute(text("DROP TABLE IF EXISTS stg_workout_activity"))
    daily = df.groupby(["date","activity_type"], as_index=False).agg(
        workout_count=("participant_id","size"), active_participants=("participant_id","nunique"),
        avg_duration=("duration_minutes","mean"), avg_calories=("calories_burned","mean")
    ).rename(columns={"date":"activity_date"})
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM daily_activity_aggregate"))
        conn.execute(text("DELETE FROM participant_graph_metrics"))
    daily.to_sql("daily_activity_aggregate", engine, if_exists="append", index=False, chunksize=1000, method="multi")
    gm = graph_metrics[["participant_id","degree_centrality","betweenness_centrality","community_id"]]
    gm.to_sql("participant_graph_metrics", engine, if_exists="append", index=False, chunksize=1000, method="multi")
    print(f"Loaded {len(fact):,} activity records and {len(gm):,} graph metric rows into PostgreSQL.")
