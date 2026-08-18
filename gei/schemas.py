from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class RawSnapshot:
    raw_snapshot_id: str
    source_id: str
    source_dataset_id: str
    source_indicator_id: str
    retrieved_at: str
    path: str
    record_count: int
    checksum_sha256: str
    dataset_version: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CanonicalObservation:
    observation_id: str
    country_id: str
    iso3: str
    reference_period: str
    year: int
    metric_id: str
    value: Optional[float]
    raw_value: Optional[float]
    modeled_value: Optional[float]
    unit: str
    frequency: str
    source_id: str
    source_dataset_id: str
    source_indicator_id: str
    retrieved_at: str
    raw_snapshot_id: str
    raw_record_index: int
    transformation_id: str
    pipeline_run_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RejectedObservation:
    source_indicator_id: str
    raw_record_index: int
    reason: str
    raw_country_code: Optional[str] = None
    raw_reference_period: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

