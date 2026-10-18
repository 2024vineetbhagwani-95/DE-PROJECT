# Optional Airflow orchestration

The DAG `fitgraph_synthetic_fitness_etl` is an on-demand workflow with three tasks:
1. Generate a deterministic synthetic CSV (600 fictional participants, 2025).
2. Run the full Pandas ETL, data quality checks, graph metrics and behavior analytics.
3. Load cleaned activity data and participant metrics into PostgreSQL.

Configure `FITGRAPH_ROOT` to the mounted project path and `DATABASE_URL` for PostgreSQL. Mount the project folder into Airflow scheduler/worker containers. Install the packages in `pipeline/requirements.txt` in the Airflow execution environment. Start with the local ETL commands in the main README before enabling Airflow.
