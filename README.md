# Multimodal Recommender System Enhancement for Netflix

Welcome to the Multimodal Recommender System Enhancement project for Netflix! This repository houses cutting-edge work aimed at improving how Netflix recommends content to its users by leveraging multiple data types, including text, images, and videos.

## Overview

This project focuses on integrating state-of-the-art machine learning models across various domains such as Natural Language Processing (NLP), Computer Vision (CV), and Reinforcement Learning (RL) to build a highly efficient and personalized recommendation system. Our goal is to deliver an even more engaging user experience by providing relevant content recommendations tailored to individual preferences.

## Data Engineering Architecture (added for internship storytelling)
- **Raw ingestion:** synthetic Netflix-style viewing events stored at `data/sample/synthetic_viewing_history.csv`.
- **Warehouse layer:** DuckDB star schema with `dim_users`, `dim_titles`, `fact_views`, plus feature tables for engagement and popularity.
- **Model training:** baseline popularity and user-based collaborative filtering running against the warehouse.
- **Outputs & analytics:** recommendations and metrics saved to `outputs/`, with SQL examples under `sql/` and an analysis script in `analysis/`.
- **Data storytelling UI:** React + Chart.js dashboard in `frontend/` for showcasing the recommendations visually.

## Why this demonstrates Netflix-ready data engineering
- Clear ETL boundaries (`extract`, `load`, `transform`, `feature_engineering`, `train_models`, `evaluate_models`) with logging and type hints in `src/netflix_recommender/data_pipeline.py`.
- Warehouse-style modeling in DuckDB and reusable SQL stored in `sql/engagement_queries.sql` for engagement analysis.
- Baseline recommenders (`popularity`, `user-based CF`) that highlight experimentation velocity on top of the warehouse.
- Automated quality via `pytest` (`tests/`), and GitHub Actions workflow (`.github/workflows/ci.yml`) to run the suite.
- Front-end storytelling with a React dashboard (`frontend/`) to showcase recommendations to stakeholders.

## Quickstart
1. **Clone & install**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```
2. **Run tests**
```bash
pytest -q
```
3. **Run the end-to-end pipeline**
```bash
python -m netflix_recommender.run_pipeline
```
4. **Inspect outputs**
   - `outputs/recommendations.csv` with top titles per user and model.
   - `outputs/metrics.json` with precision@k and coverage.
   - `analysis/recommendation_analysis.py` to print a human-readable summary.

## Sample output (from the synthetic dataset)
```
Pipeline metrics: {
  "precision_at_k": 0.5,
  "test_users": 5
}

Sample recommendations:
  user_id title_id  rank       model
0     u1      s1     1  popularity
1     u1      s3     2  popularity
2     u1      s4     3  popularity
```

## Front-end data storytelling (React)
- Navigate to `frontend/`, run `npm install` then `npm run dev` to launch the dashboard at http://localhost:5173.
- The dashboard reads `frontend/public/sample_recommendations.json` by default; replace it with `outputs/recommendations.csv` converted to JSON for live data.
- Components live in `frontend/src/` and use Chart.js for quick visuals (coverage, precision badge, per-user tiles).
