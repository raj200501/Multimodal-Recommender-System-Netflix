"""Data quality checks for the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

import pandas as pd


@dataclass
class QualityCheckResult:
    name: str
    passed: bool
    message: str


@dataclass
class QualityReport:
    dataset: str
    checks: List[QualityCheckResult] = field(default_factory=list)

    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_dict(self) -> Dict[str, object]:
        return {
            "dataset": self.dataset,
            "passed": self.passed(),
            "checks": [check.__dict__ for check in self.checks],
        }


@dataclass
class DataQualityConfig:
    min_rows: int = 1
    required_columns: Iterable[str] = field(default_factory=list)
    numeric_ranges: Dict[str, tuple[float, float]] = field(default_factory=dict)


def check_min_rows(df: pd.DataFrame, min_rows: int) -> QualityCheckResult:
    if len(df) >= min_rows:
        return QualityCheckResult("min_rows", True, f"row_count={len(df)}")
    return QualityCheckResult("min_rows", False, f"row_count={len(df)} < {min_rows}")


def check_required_columns(
    df: pd.DataFrame, columns: Iterable[str]
) -> QualityCheckResult:
    missing = [column for column in columns if column not in df.columns]
    if not missing:
        return QualityCheckResult("required_columns", True, "all columns present")
    return QualityCheckResult(
        "required_columns", False, f"missing: {', '.join(missing)}"
    )


def check_numeric_ranges(
    df: pd.DataFrame, ranges: Dict[str, tuple[float, float]]
) -> List[QualityCheckResult]:
    results: List[QualityCheckResult] = []
    for column, (low, high) in ranges.items():
        if column not in df.columns:
            results.append(
                QualityCheckResult(f"range:{column}", False, "column missing")
            )
            continue
        series = df[column].dropna()
        if series.empty:
            results.append(QualityCheckResult(f"range:{column}", False, "no values"))
            continue
        out_of_bounds = series[(series < low) | (series > high)]
        if out_of_bounds.empty:
            results.append(QualityCheckResult(f"range:{column}", True, "within range"))
        else:
            results.append(
                QualityCheckResult(
                    f"range:{column}",
                    False,
                    f"out_of_bounds={len(out_of_bounds)}",
                )
            )
    return results


def run_quality_checks(
    df: pd.DataFrame, config: DataQualityConfig, dataset: str
) -> QualityReport:
    report = QualityReport(dataset=dataset)
    report.checks.append(check_min_rows(df, config.min_rows))
    if config.required_columns:
        report.checks.append(check_required_columns(df, config.required_columns))
    if config.numeric_ranges:
        report.checks.extend(check_numeric_ranges(df, config.numeric_ranges))
    return report
