from datetime import datetime, timedelta
import os
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator

ROOT = Path(os.getenv("FITGRAPH_ROOT", "/opt/fitgraph"))
INPUT = ROOT / "data" / "raw" / "synthetic_fitness_dataset.csv"
OUTPUT = ROOT / "data" / "processed"

def generate_data():
    import sys
    sys.path.insert(0, str(ROOT))
    from pipeline.generate_synthetic import generate
    generate(str(INPUT), participants=600, year=2025, seed=42)

def run_etl():
    import sys
    sys.path.insert(0, str(ROOT))
    from pipeline.run_pipeline import main
    import sys as _sys
    previous = _sys.argv[:]
    try:
        _sys.argv = ["run_pipeline", "--input", str(INPUT), "--output", str(OUTPUT), "--skip-postgres"]
        main()
    finally:
        _sys.argv = previous

def load_warehouse():
    import sys
    sys.path.insert(0, str(ROOT))
    import pandas as pd
    from pipeline.transform import transform, build_profiles
    from pipeline.graph import build_similarity_graph
    from pipeline.load_postgres import load_warehouse as load
    raw = pd.read_csv(INPUT)
    cleaned, _ = transform(raw)
    profiles = build_profiles(cleaned)
    edges, metrics, graph = build_similarity_graph(profiles)
    load(cleaned, profiles.merge(metrics, on="participant_id", how="left"), metrics)

with DAG(
    dag_id="fitgraph_synthetic_fitness_etl",
    description="Generate synthetic data, transform and analyze it, then load the PostgreSQL warehouse",
    start_date=datetime(2025, 1, 1), schedule=None, catchup=False,
    default_args={"owner":"fitgraph", "retries":1, "retry_delay":timedelta(minutes=2)},
    tags=["fitgraph", "synthetic-data", "etl", "analytics"],
) as dag:
    synthetic_source = PythonOperator(task_id="generate_synthetic_source", python_callable=generate_data)
    transform_and_analyze = PythonOperator(task_id="transform_and_analyze", python_callable=run_etl)
    warehouse_load = PythonOperator(task_id="warehouse_load", python_callable=load_warehouse)
    synthetic_source >> transform_and_analyze >> warehouse_load
