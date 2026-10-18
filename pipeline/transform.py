from __future__ import annotations
import pandas as pd
import numpy as np

REQUIRED = [
    "participant_id", "date", "age", "gender", "height_cm", "weight_kg",
    "activity_type", "duration_minutes", "intensity", "calories_burned",
    "avg_heart_rate", "hours_sleep", "stress_level", "daily_steps",
    "hydration_level", "bmi", "resting_heart_rate",
    "blood_pressure_systolic", "blood_pressure_diastolic",
    "health_condition", "smoking_status", "fitness_level"
]

def transform(raw: pd.DataFrame):
    missing_columns = sorted(set(REQUIRED) - set(raw.columns))
    if missing_columns:
        raise ValueError(f"Source schema is missing required columns: {missing_columns}")
    df = raw[REQUIRED].copy()
    rows_in = len(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    numeric = [c for c in REQUIRED if c not in {
        "date", "gender", "activity_type", "intensity", "smoking_status", "health_condition"
    }]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Critical fields required for activity fact records.
    critical = ["participant_id", "date", "activity_type", "duration_minutes"]
    missing_critical = int(df[critical].isna().any(axis=1).sum())
    df = df.dropna(subset=critical)
    # Reject impossible duration/steps values; keep optional health-condition values nullable.
    invalid = (
        (df["duration_minutes"] <= 0) |
        (df["duration_minutes"] > 1440) |
        (df["daily_steps"] < 0) |
        (df["avg_heart_rate"] < 0)
    )
    rejected_range = int(invalid.sum())
    df = df.loc[~invalid].copy()
    df["participant_id"] = df["participant_id"].astype("int64")
    df["date"] = df["date"].dt.date.astype(str)
    df["activity_type"] = df["activity_type"].astype(str).str.strip().str.title()
    df["intensity"] = df["intensity"].fillna("Unknown").astype(str).str.strip().str.title()
    df["gender"] = df["gender"].fillna("Unknown").astype(str).str.strip()
    df["smoking_status"] = df["smoking_status"].fillna("Unknown").astype(str).str.strip()
    df = df.drop_duplicates()
    quality = {
        "rows_in": int(rows_in),
        "rows_out": int(len(df)),
        "missing_critical_rows_removed": missing_critical,
        "invalid_range_rows_removed": rejected_range,
        "duplicate_rows_removed": int(rows_in - missing_critical - rejected_range - len(df)),
        "health_condition_nulls_preserved": int(df["health_condition"].isna().sum()),
        "critical_nulls_remaining": int(df[critical].isna().sum().sum()),
        "status": "SUCCESS",
    }
    return df, quality

def build_profiles(df: pd.DataFrame):
    def mode_or_unknown(s):
        m = s.mode()
        return m.iloc[0] if len(m) else "Unknown"
    profiles = df.groupby("participant_id").agg(
        age=("age", "first"), gender=("gender", "first"),
        avg_duration=("duration_minutes", "mean"),
        avg_calories=("calories_burned", "mean"),
        avg_heart_rate=("avg_heart_rate", "mean"),
        avg_sleep=("hours_sleep", "mean"),
        avg_steps=("daily_steps", "mean"),
        avg_stress=("stress_level", "mean"),
        avg_hydration=("hydration_level", "mean"),
        avg_fitness_level=("fitness_level", "mean"),
        workouts=("activity_type", "size"),
        dominant_activity=("activity_type", mode_or_unknown),
        avg_intensity=("intensity", mode_or_unknown)
    ).reset_index()
    return profiles
