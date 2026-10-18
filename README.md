# FitGraph — Fitness Analytics & Network Intelligence

FitGraph is a data engineering project that transforms **synthetic fitness activity data** into actionable insights using ETL pipelines, analytics, graph analysis, and interactive visualizations.

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Data Processing | Pandas, NumPy, Scikit-learn, NetworkX |
| Database | PostgreSQL |
| Data Engineering | ETL, data validation, data quality checks |
| Data Warehouse | SQL |
| Orchestration | Apache Airflow |
| Deployment | Docker, Docker Compose |
| Visualization | Interactive charts and fitness analytics |

## Key Features

- **Synthetic Data Generation:** Generates realistic fitness activity records for analysis.
- **ETL Pipeline:** Extracts, validates, cleans, and transforms the data.
- **Fitness Analytics:** Analyzes workout trends, consistency, intensity, and recovery.
- **Network Analytics:** Explores relationships between participants based on activity patterns.
- **Data Warehouse:** Organizes structured fitness data for analytical queries.
- **Interactive Dashboard:** Presents insights through a modern web interface.

## Getting Started

### Prerequisites

Install the following:

- Python 3.10 or later
- Node.js 18 or later
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/2024vineetbhagwani-95/DE-PROJECT.git
cd DE-PROJECT
```

### 2. Set Up Python

Run these commands from the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r pipeline/requirements.txt
```

### 3. Generate Synthetic Data and Run the ETL Pipeline

```bash
python -m pipeline.generate_synthetic --output data/raw/synthetic_fitness_dataset.csv --participants 800 --year 2025 --seed 123

python -m pipeline.run_pipeline --input data/raw/synthetic_fitness_dataset.csv --output data/processed --skip-postgres
```

This generates synthetic fitness records and produces processed analytics outputs without loading data into PostgreSQL.

### 4. Start the Backend

Open a new terminal at the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 5. Start the Frontend

Open another terminal at the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your browser.

## Project Structure

```text
DE-PROJECT/
├── frontend/       # React dashboard
├── backend/        # FastAPI backend
├── pipeline/       # ETL and analytics
├── data/
│   ├── raw/        # Generated source data
│   └── processed/  # Analytics outputs
├── airflow/        # Workflow orchestration
├── sql/            # Warehouse SQL
├── docker-compose.yml
└── README.md
```


