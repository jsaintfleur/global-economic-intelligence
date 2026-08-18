from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PipelineManifest:
    pipeline_run_id: str
    started_at: str
    completed_at: Optional[str]
    status: str
    source_ids: list[str]
    indicators_requested: list[str]
    countries_requested: str
    raw_observations_received: int = 0
    accepted_observations: int = 0
    rejected_observations: int = 0
    missing_observations: int = 0
    duplicate_observations: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    raw_snapshots: list[dict] = field(default_factory=list)
    output_files: list[str] = field(default_factory=list)
    code_version: str = "0.2.0"
    schema_version: str = "1.0"

    def write(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.pipeline_run_id}.json"
        path.write_text(json.dumps(asdict(self), indent=2, sort_keys=True), encoding="utf-8")
        return path
