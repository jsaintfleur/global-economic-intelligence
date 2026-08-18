from __future__ import annotations

import hashlib
import json
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .config import WORLD_BANK_BASE
from .schemas import RawSnapshot, RejectedObservation


@dataclass
class AdapterResult:
    records: list[dict]
    snapshot: RawSnapshot
    rejected: list[RejectedObservation]
    warnings: list[str]


class SourceAdapter(ABC):
    """Contract implemented by every upstream data source."""

    source_id: str
    source_dataset_id: str

    @abstractmethod
    def fetch_indicator(self, indicator_id: str, start: int, end: int, retrieved_at: str) -> AdapterResult:
        raise NotImplementedError

    @abstractmethod
    def fetch_countries(self, retrieved_at: str) -> AdapterResult:
        raise NotImplementedError


class WorldBankAdapter(SourceAdapter):
    source_id = "world_bank_wdi"
    source_dataset_id = "world_development_indicators"

    def __init__(self, raw_root: Path, timeout: int = 60, retries: int = 3, opener: Callable = urllib.request.urlopen):
        self.raw_root = raw_root
        self.timeout = timeout
        self.retries = retries
        self.opener = opener

    def _request_pages(self, path: str, params: dict[str, Any]) -> list[dict]:
        params = {**params, "format": "json", "per_page": 20000}
        rows: list[dict] = []
        page = 1
        while True:
            url = f"{WORLD_BANK_BASE}/{path}?{urllib.parse.urlencode({**params, 'page': page})}"
            payload = self._request_json(url)
            if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[0], dict):
                raise ValueError(f"World Bank schema changed for {path}")
            rows.extend(payload[1] or [])
            pages = int(payload[0].get("pages", 1))
            if page >= pages:
                break
            page += 1
        return rows

    def _request_json(self, url: str) -> Any:
        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                with self.opener(url, timeout=self.timeout) as response:
                    return json.load(response)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt + 1 < self.retries:
                    time.sleep((2 ** attempt) + random.random() * 0.1)
        raise RuntimeError(f"Source request failed after {self.retries} attempts") from last_error

    def fetch_countries(self, retrieved_at: str) -> AdapterResult:
        return self._fetch("country", {}, "country_dimension", retrieved_at)

    def fetch_indicator(self, indicator_id: str, start: int, end: int, retrieved_at: str) -> AdapterResult:
        return self._fetch(f"country/all/indicator/{indicator_id}", {"date": f"{start}:{end}"}, indicator_id, retrieved_at)

    def _fetch(self, path: str, params: dict, indicator_id: str, retrieved_at: str) -> AdapterResult:
        if not re.fullmatch(r"[A-Za-z0-9._-]+",indicator_id):
            raise ValueError("Unsafe source indicator identifier")
        snapshot_dir = self.raw_root / retrieved_at[:10]
        filename = f"{indicator_id}_{params.get('date', 'all').replace(':', '_')}.json"
        target = snapshot_dir / filename
        legacy = self.raw_root / ("countries.json" if indicator_id == "country_dimension" else f"{indicator_id}.json")
        warnings: list[str] = []
        if target.exists():
            raw_bytes = target.read_bytes(); records = json.loads(raw_bytes); warnings.append("cache_hit:dated_snapshot")
        elif legacy.exists():
            raw_bytes = legacy.read_bytes(); records = json.loads(raw_bytes); warnings.append("cache_hit:legacy_snapshot")
            snapshot_dir.mkdir(parents=True, exist_ok=True); target.write_bytes(raw_bytes)
        else:
            records = self._request_pages(path, params)
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            raw_bytes = json.dumps(records, ensure_ascii=False, separators=(",", ":")).encode()
            target.write_bytes(raw_bytes)
        checksum = hashlib.sha256(raw_bytes).hexdigest()
        snapshot_id = f"raw_{self.source_id}_{indicator_id}_{checksum[:16]}"
        snapshot = RawSnapshot(snapshot_id, self.source_id, self.source_dataset_id, indicator_id, retrieved_at, str(target.relative_to(self.raw_root.parent.parent)), len(records), checksum)
        return AdapterResult(records, snapshot, [], warnings)
