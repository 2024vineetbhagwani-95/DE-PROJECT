from __future__ import annotations
import argparse, json, os
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
from pipeline.transform import transform, build_profiles
from pipeline.graph import build_similarity_graph
from pipeline.load_postgres import load_warehouse
from pipeline.insights import build_behavior_insights

def main():
    parser = argparse.ArgumentParser(description="Run the FitGraph ETL and graph analytics pipeline.")
    parser.add_argument("--input", default="data/raw/synthetic_fitness_dataset.csv")
    parser.add_argument("--output", default="data/processed")
    parser.add_argument("--skip-postgres", action="store_true")
    args = parser.parse_args()
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    print(f"[1/5] Extracting {args.input}")
    raw = pd.read_csv(args.input)
    print(f"Read {len(raw):,} rows.")
    print("[2/5] Validating and transforming")
    df, quality = transform(raw)
    print(f"Kept {len(df):,}; removed {quality['rows_in']-quality['rows_out']:,} rows.")
    print("[3/5] Building participant profiles and graph")
    profiles = build_profiles(df)
    edges, metrics, graph = build_similarity_graph(profiles)
    profiles = profiles.merge(metrics, on="participant_id", how="left")
    print(f"Graph: {graph.number_of_nodes():,} nodes, {graph.number_of_edges():,} edges.")
    print("[4/5] Generating analytics")
    df["date_dt"] = pd.to_datetime(df["date"])
    df["month"] = df["date_dt"].dt.strftime("%Y-%m")
    activity = df.groupby("activity_type", as_index=False).agg(
        workouts=("participant_id","size"), avg_duration=("duration_minutes","mean"),
        avg_calories=("calories_burned","mean"), avg_heart_rate=("avg_heart_rate","mean")
    ).sort_values("workouts", ascending=False)
    monthly = df.groupby("month", as_index=False).agg(workouts=("participant_id","size"),
        avg_duration=("duration_minutes","mean"), calories=("calories_burned","sum"),
        active_participants=("participant_id","nunique"))
    weekday = df.assign(weekday=df["date_dt"].dt.day_name()).groupby("weekday", as_index=False).agg(
        workouts=("participant_id","size"), avg_duration=("duration_minutes","mean"))
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    weekday["sort"] = weekday["weekday"].map({v:i for i,v in enumerate(order)})
    weekday = weekday.sort_values("sort").drop(columns="sort")
    intensity = df.groupby("intensity", as_index=False).size().rename(columns={"size":"workouts"})
    summary = {
        "records": int(len(df)), "participants": int(df["participant_id"].nunique()),
        "activity_types": int(df["activity_type"].nunique()),
        "date_start": str(df["date_dt"].min().date()), "date_end": str(df["date_dt"].max().date()),
        "avg_duration": round(float(df["duration_minutes"].mean()),2),
        "avg_calories": round(float(df["calories_burned"].mean()),2),
        "avg_steps": round(float(df["daily_steps"].mean()),2),
        "avg_sleep": round(float(df["hours_sleep"].mean()),2),
        "graph_nodes": int(graph.number_of_nodes()), "graph_edges": int(graph.number_of_edges()),
        "graph_note": "Edges represent inferred fitness similarity, not real social relationships."
    }
    (out/"summary.json").write_text(json.dumps(summary, indent=2))
    behavior = build_behavior_insights(df, out)
    print(f"Behavior insights: {len(behavior['retention'])} months, {len(behavior['consistency'])} consistency bands, {len(behavior['recovery'])} recovery bands.")
    activity.to_json(out/"activity_breakdown.json", orient="records", indent=2)
    monthly.to_json(out/"monthly_trends.json", orient="records", indent=2)
    weekday.to_json(out/"weekday_trends.json", orient="records", indent=2)
    intensity.to_json(out/"intensity_breakdown.json", orient="records", indent=2)
    profiles.to_json(out/"participant_profiles.json", orient="records", indent=2)
    profiles.to_csv(out/"participant_profiles.csv", index=False)
    edges.to_json(out/"graph_edges.json", orient="records", indent=2)
    report = {**quality, "status":"SUCCESS", "generated_at":datetime.now(timezone.utc).isoformat(),
              "graph_nodes":int(graph.number_of_nodes()), "graph_edges":int(graph.number_of_edges())}
    (out/"quality_report.json").write_text(json.dumps(report, indent=2))
    print("[5/5] Loading warehouse")
    if args.skip_postgres:
        print("Skipped because --skip-postgres was passed.")
    else:
        load_warehouse(df, profiles, metrics)
    print("FitGraph ETL completed successfully.")

if __name__ == "__main__":
    main()
