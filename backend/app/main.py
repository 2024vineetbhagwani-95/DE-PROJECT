from pathlib import Path
import json
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(os.getenv("FITGRAPH_ROOT", Path(__file__).resolve().parents[2]))
if not (ROOT / "data" / "processed").exists() and (Path(__file__).resolve().parents[1] / "data" / "processed").exists():
    ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

app = FastAPI(title="FitGraph API", version="1.0.0",
              description="Synthetic fitness behavior analytics and data engineering pipeline.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

def load_json(name):
    path = DATA / name
    if not path.exists():
        raise HTTPException(503, f"Missing processed file {name}. Run the ETL pipeline first.")
    return json.loads(path.read_text(encoding="utf-8"))

@app.get("/health")
def health():
    return {"status": "ok", "service": "fitgraph-api"}

@app.get("/api/insights/behavior")
def behavior_insights():
    return load_json("behavior_insights.json")

@app.get("/api/summary")
def summary():
    return load_json("summary.json")

@app.get("/api/activities")
def activities():
    return load_json("activity_breakdown.json")

@app.get("/api/trends/monthly")
def monthly_trends():
    return load_json("monthly_trends.json")

@app.get("/api/trends/weekday")
def weekday_trends():
    return load_json("weekday_trends.json")

@app.get("/api/intensity")
def intensity_breakdown():
    return load_json("intensity_breakdown.json")

@app.get("/api/participants")
def participants(q: Optional[str] = None, activity: Optional[str] = None,
                 limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    rows = load_json("participant_profiles.json")
    if q:
        rows = [r for r in rows if q.lower() in str(r["participant_id"]).lower()]
    if activity and activity != "All":
        rows = [r for r in rows if r["dominant_activity"] == activity]
    rows.sort(key=lambda r: r.get("workouts", 0), reverse=True)
    return {"total": len(rows), "items": rows[offset:offset+limit]}

@app.get("/api/participants/{participant_id}")
def participant_detail(participant_id: int):
    rows = load_json("participant_profiles.json")
    for row in rows:
        if int(row["participant_id"]) == participant_id:
            return row
    raise HTTPException(404, "Participant not found")

@app.get("/api/graph")
def graph(limit_nodes: int = Query(350, ge=30, le=800), limit_edges: int = Query(900, ge=50, le=3000)):
    nodes = load_json("participant_profiles.json")
    edges = load_json("graph_edges.json")
    # Deterministic sample for responsive rendering; highest workout-count participants are prioritized.
    nodes.sort(key=lambda r: (r.get("workouts", 0), -int(r["participant_id"])), reverse=True)
    selected = nodes[:limit_nodes]
    ids = {int(n["participant_id"]) for n in selected}
    filtered_edges = [e for e in edges if int(e["source"]) in ids and int(e["target"]) in ids]
    filtered_edges.sort(key=lambda e: e.get("weight", 0), reverse=True)
    return {
        "nodes": [{"id": int(n["participant_id"]), "activity": n["dominant_activity"],
                   "workouts": int(n["workouts"]), "fitness": round(float(n.get("avg_fitness_level") or 0), 3)}
                  for n in selected],
        "edges": filtered_edges[:limit_edges],
        "note": "Edges are inferred fitness similarity, not real social relationships."
    }

@app.get("/api/pipeline/status")
def pipeline_status():
    summary = load_json("summary.json")
    report_path = DATA / "quality_report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {
        "status": "PRECOMPUTED", "message": "Bundled analytics were generated from the provided dataset."
    }
    return {
        "pipeline": "FitGraph Synthetic Fitness ETL",
        "status": report.get("status", "PRECOMPUTED"),
        "last_run": report.get("generated_at", "Bundled dataset snapshot"),
        "source_records": summary["records"],
        "participants": summary["participants"],
        "quality_report": report,
        "stages": [
            {"name": "Extract", "status": "success", "detail": "Read the synthetic fitness CSV source"},
            {"name": "Validate & transform", "status": "success", "detail": "Schema, types, quality checks and feature engineering"},
            {"name": "Graph analytics", "status": "success", "detail": "Goal adherence, retention, consistency, recovery and training-load features"},
            {"name": "Warehouse load", "status": "configured", "detail": "PostgreSQL star schema loader; requires DATABASE_URL"}
        ]
    }
