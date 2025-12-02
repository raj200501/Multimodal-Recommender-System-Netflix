"""DuckDB helper utilities for the Netflix recommender demo."""
from pathlib import Path
from typing import Iterable, List

import duckdb


def get_connection(db_path: Path) -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection pointing to the provided path."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(database=str(db_path))


def write_dataframe(
    conn: duckdb.DuckDBPyConnection, df, table_name: str, mode: str = "replace"
) -> None:
    """Write a pandas DataFrame into DuckDB."""
    if mode not in {"replace", "append"}:
        raise ValueError("mode must be 'replace' or 'append'")
    if mode == "replace":
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    else:
        conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")


def run_queries(conn: duckdb.DuckDBPyConnection, queries: Iterable[str]) -> List:
    """Execute a list of SQL queries and return the results."""
    results = []
    for query in queries:
        results.append(conn.execute(query).fetchall())
    return results


def run_query_file(conn: duckdb.DuckDBPyConnection, sql_file: Path) -> List:
    """Execute queries from a SQL file split by semicolons."""
    content = sql_file.read_text()
    queries = [q.strip() for q in content.split(";") if q.strip()]
    return run_queries(conn, queries)
