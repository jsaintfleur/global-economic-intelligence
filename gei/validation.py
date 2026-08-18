from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable


REQUIRED_METRIC_FIELDS = {
    "metric_id", "display_name", "source_id", "source_dataset_id", "source_indicator_id",
    "unit", "frequency", "value_type", "formatting", "transformation", "missing_data_policy",
}
REQUIRED_OBSERVATION_FIELDS = {
    "observation_id", "country_id", "iso3", "reference_period", "year", "metric_id", "value",
    "unit", "frequency", "source_id", "source_dataset_id", "source_indicator_id", "retrieved_at",
    "raw_snapshot_id", "raw_record_index", "transformation_id", "pipeline_run_id",
}


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    def require_valid(self) -> None:
        if self.errors:
            raise ValueError("Validation failed: " + "; ".join(self.errors[:10]))


def validate_metric_registry(metrics: list[dict]) -> ValidationReport:
    report = ValidationReport()
    ids = [m.get("metric_id") for m in metrics]
    duplicates = [key for key, count in Counter(ids).items() if key and count > 1]
    if duplicates:
        report.errors.append(f"duplicate metric IDs: {duplicates}")
    for index, metric in enumerate(metrics):
        missing = REQUIRED_METRIC_FIELDS - metric.keys()
        if missing:
            report.errors.append(f"metric[{index}] missing fields: {sorted(missing)}")
        if metric.get("transformation") not in {"identity", "cagr", "pct_change", "rebase"}:
            report.errors.append(f"metric[{index}] malformed transformation mapping")
    return report


def validate_observations(observations: Iterable[dict], countries: Iterable[dict], metrics: Iterable[dict]) -> ValidationReport:
    report = ValidationReport()
    country_ids = {c["iso3"] for c in countries}
    metric_ids = {m["metric_id"] for m in metrics}
    keys: set[tuple[str, int, str]] = set()
    observation_ids: set[str] = set()
    for index, row in enumerate(observations):
        missing = REQUIRED_OBSERVATION_FIELDS - row.keys()
        if missing:
            report.errors.append(f"observation[{index}] missing fields: {sorted(missing)}")
            continue
        iso3 = row["iso3"]
        if not isinstance(iso3, str) or len(iso3) != 3 or not iso3.isupper():
            report.errors.append(f"observation[{index}] invalid ISO3: {iso3!r}")
        if iso3 not in country_ids:
            report.errors.append(f"observation[{index}] unknown country: {iso3}")
        if row["metric_id"] not in metric_ids:
            report.errors.append(f"observation[{index}] orphan metric: {row['metric_id']}")
        if not isinstance(row["year"], int) or not 1800 <= row["year"] <= 2200:
            report.errors.append(f"observation[{index}] invalid year: {row['year']!r}")
        value = row["value"]
        if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
            report.errors.append(f"observation[{index}] nonnumeric value")
        if not row["source_id"] or not row["raw_snapshot_id"] or not row["pipeline_run_id"]:
            report.errors.append(f"observation[{index}] missing provenance")
        key = (iso3, row["year"], row["metric_id"])
        if key in keys:
            report.errors.append(f"duplicate observation key: {key}")
        keys.add(key)
        if row["observation_id"] in observation_ids:
            report.errors.append(f"duplicate observation ID: {row['observation_id']}")
        observation_ids.add(row["observation_id"])
    return report
