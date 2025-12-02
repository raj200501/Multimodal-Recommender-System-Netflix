"""Command-line entrypoint for the Netflix recommender demo."""
from netflix_recommender.data_pipeline import run_pipeline


if __name__ == "__main__":
    run_pipeline()
