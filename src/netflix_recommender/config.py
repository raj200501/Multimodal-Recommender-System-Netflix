"""Configuration utilities for the Netflix recommender demo."""
from pathlib import Path


def get_project_root() -> Path:
    """Return the project root path."""
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = get_project_root()
DATA_PATH = PROJECT_ROOT / "data" / "sample" / "synthetic_viewing_history.csv"
DB_PATH = PROJECT_ROOT / "outputs" / "netflix_duckdb.db"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SQL_DIR = PROJECT_ROOT / "sql"
DEFAULT_TOP_K = 5


def ensure_output_dir() -> None:
    """Ensure the output directory exists."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
