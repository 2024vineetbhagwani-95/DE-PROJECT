-- FitGraph warehouse schema (the Python loader can create these tables automatically)
CREATE TABLE IF NOT EXISTS dim_participant (
  participant_id BIGINT PRIMARY KEY, age INTEGER, gender TEXT, height_cm DOUBLE PRECISION,
  weight_kg DOUBLE PRECISION, bmi DOUBLE PRECISION, smoking_status TEXT
);
CREATE TABLE IF NOT EXISTS dim_workout_type (activity_type TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS dim_date (
  date_key DATE PRIMARY KEY, year INTEGER, month INTEGER, day INTEGER, weekday TEXT
);
CREATE TABLE IF NOT EXISTS fact_workout_activity (
  participant_id BIGINT NOT NULL, activity_date DATE NOT NULL, activity_type TEXT NOT NULL,
  duration_minutes INTEGER, intensity TEXT, calories_burned DOUBLE PRECISION,
  avg_heart_rate DOUBLE PRECISION, hours_sleep DOUBLE PRECISION, stress_level INTEGER,
  daily_steps INTEGER, hydration_level DOUBLE PRECISION, fitness_level DOUBLE PRECISION,
  source_hash TEXT, PRIMARY KEY (participant_id, activity_date)
);
CREATE INDEX IF NOT EXISTS idx_fact_activity_date ON fact_workout_activity(activity_date);
CREATE INDEX IF NOT EXISTS idx_fact_activity_type ON fact_workout_activity(activity_type);
CREATE TABLE IF NOT EXISTS daily_activity_aggregate (
  activity_date DATE NOT NULL, activity_type TEXT NOT NULL, workout_count BIGINT,
  active_participants BIGINT, avg_duration DOUBLE PRECISION, avg_calories DOUBLE PRECISION,
  PRIMARY KEY (activity_date, activity_type)
);
CREATE TABLE IF NOT EXISTS participant_graph_metrics (
  participant_id BIGINT PRIMARY KEY, degree_centrality DOUBLE PRECISION,
  betweenness_centrality DOUBLE PRECISION, community_id INTEGER
);
