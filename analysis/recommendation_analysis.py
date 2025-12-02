"""Simple analysis of recommendation outputs."""
import json
from pathlib import Path

import pandas as pd

from netflix_recommender import config


def load_outputs(output_dir: Path = config.OUTPUT_DIR) -> tuple[pd.DataFrame, dict]:
    recommendations = pd.read_csv(output_dir / "recommendations.csv")
    metrics = json.loads((output_dir / "metrics.json").read_text())
    return recommendations, metrics


def summarize() -> None:
    recommendations, metrics = load_outputs()
    print("Pipeline metrics:", json.dumps(metrics, indent=2))
    sample = recommendations.groupby(["user_id", "model"]).head(3)
    print("\nSample recommendations:")
    print(sample)


if __name__ == "__main__":
    summarize()
