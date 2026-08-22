from __future__ import annotations

import csv
import gzip
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .universe import UniverseGDPObservation
from .ids import stable_id


_FISCAL_YEAR = re.compile(r"^FY(\d{4})/\d{2}$")


def normalize_actual_boundary(value: str) -> int:
    value = (value or "").strip()
    if value.isdigit() and len(value) == 4:
        return int(value)
    match = _FISCAL_YEAR.fullmatch(value)
    if match:
        return int(match.group(1))
    raise ValueError(f"unsupported WEO actual-boundary value: {value!r}")


def load_reference_classes(path: Path) -> dict[str, str]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    classes: dict[str, str] = {}
    for section, rows in document.items():
        if section == "codelist" or not isinstance(rows, list):
            continue
        for row in rows:
            code = row["code"]
            if code in classes:
                raise ValueError(f"duplicate IMF reference code: {code}")
            classes[code] = section
    expected = document["codelist"]["total_codes"]
    classified_codelist = sum(
        1 for classification in classes.values() if classification != "undeclared_observed"
    )
    if classified_codelist != expected:
        raise ValueError(
            f"IMF reference list incomplete: expected {expected}, "
            f"classified {classified_codelist}"
        )
    return classes


def load_eligibility(path: Path) -> dict[str, dict]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    return document["entities"]


@dataclass(frozen=True)
class WEOUniverseData:
    observations: tuple[UniverseGDPObservation, ...]
    boundaries: dict[str, tuple[str, int]]
    publication_date: str
    update_date: str
    pool_count: int
    pool_actual_count: int


def read_ngdpd_snapshot(
    snapshot_path: Path,
    reference_path: Path,
    eligibility_path: Path,
) -> WEOUniverseData:
    classes = load_reference_classes(reference_path)
    observations: list[UniverseGDPObservation] = []
    boundaries: dict[str, tuple[str, int]] = {}
    publication_dates: set[str] = set()
    update_dates: set[str] = set()
    pool_actual_count = 0

    with gzip.open(snapshot_path, "rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            code = (row.get("COUNTRY") or "").strip()
            if code not in classes:
                raise ValueError(f"undeclared IMF country-dimension code: {code!r}")
            if classes[code] != "economy":
                continue
            period = (row.get("TIME_PERIOD") or "").strip()
            value = (row.get("OBS_VALUE") or "").strip()
            if not period or not value:
                continue
            if row.get("INDICATOR") != "NGDPD" or row.get("FREQUENCY") != "A":
                continue
            year = int(period)
            raw_boundary = (row.get("LATEST_ACTUAL_ANNUAL_DATA") or "").strip()
            normalized_boundary = normalize_actual_boundary(raw_boundary)
            boundaries[code] = (raw_boundary, normalized_boundary)
            publication_dates.add(row["PUBLICATION_DATE"])
            update_dates.add(row["UPDATE_DATE"])
            numeric_value = int(value)
            observations.append(
                UniverseGDPObservation(
                    analytical_entity_id=f"entity:{code}",
                    iso3=code,
                    year=year,
                    value=numeric_value,
                    source_id="imf_weo",
                    source_indicator_id="NGDPD",
                )
            )
            if normalized_boundary >= year:
                pool_actual_count += 1

    if len(publication_dates) != 1 or len(update_dates) != 1:
        raise ValueError("WEO snapshot contains inconsistent vintage metadata")
    return WEOUniverseData(
        observations=tuple(observations),
        boundaries=boundaries,
        publication_date=publication_dates.pop(),
        update_date=update_dates.pop(),
        pool_count=len(observations),
        pool_actual_count=pool_actual_count,
    )


class WEOFixtureGDPProvider:
    provider_id = "imf_weo"

    def __init__(self, data: WEOUniverseData):
        self.data = data

    def observations(self):
        return self.data.observations


def verify_metric_fixture_bundle(directory: Path) -> dict:
    manifest_path = directory / "MANIFEST.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    expected_publication = manifest["vintage"]["publication_date"]
    expected_update = manifest["vintage"]["update_date"]
    expected_window = manifest["release_window"]
    seen_indicators: set[str] = set()
    for entry in manifest["files"]:
        path = directory / entry["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(
                f"WEO fixture checksum mismatch for {entry['path']}: "
                f"expected {entry['sha256']}, got {digest}"
            )
        publication_dates: set[str] = set()
        update_dates: set[str] = set()
        indicators: set[str] = set()
        with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                publication_dates.add(row["PUBLICATION_DATE"])
                update_dates.add(row["UPDATE_DATE"])
                indicators.add(row["INDICATOR"])
                period = (row.get("TIME_PERIOD") or "").strip()
                if period and not (
                    expected_window["start_year"]
                    <= int(period)
                    <= expected_window["end_year"]
                ):
                    raise ValueError(
                        f"WEO fixture row outside release window in {entry['path']}: {period}"
                    )
        if indicators != {entry["indicator"]}:
            raise ValueError(
                f"WEO fixture indicator mismatch for {entry['path']}: {sorted(indicators)}"
            )
        if publication_dates != {expected_publication}:
            raise ValueError(
                f"WEO mixed publication vintage in {entry['path']}: "
                f"{sorted(publication_dates)}"
            )
        if update_dates != {expected_update}:
            raise ValueError(
                f"WEO mixed update vintage in {entry['path']}: {sorted(update_dates)}"
            )
        if entry["indicator"] in seen_indicators:
            raise ValueError(f"duplicate WEO metric fixture: {entry['indicator']}")
        seen_indicators.add(entry["indicator"])
    return manifest


def read_metric_fixture_observations(
    directory: Path,
    reference_path: Path,
    metrics: list[dict],
    run_id: str,
    retrieved_at: str,
    universe_reference_year: int = 2024,
    allowed_iso3: set[str] | None = None,
) -> tuple[list[dict], list[dict]]:
    manifest = verify_metric_fixture_bundle(directory)
    classes = load_reference_classes(reference_path)
    by_indicator = {
        metric["source_indicator_id"]: metric
        for metric in metrics
        if metric["source_id"] == "imf_weo"
    }
    entries = {entry["indicator"]: entry for entry in manifest["files"]}
    if set(entries) != set(by_indicator):
        raise ValueError(
            "WEO governed metric set differs from fixture set: "
            f"registry={sorted(by_indicator)}, fixtures={sorted(entries)}"
        )
    observations: list[dict] = []
    snapshots: list[dict] = []
    for indicator, metric in sorted(by_indicator.items()):
        entry = entries[indicator]
        path = directory / entry["path"]
        raw_snapshot_id = stable_id("raw", "imf_weo", indicator, entry["sha256"])
        snapshots.append(
            {
                "raw_snapshot_id": raw_snapshot_id,
                "source_id": "imf_weo",
                "source_dataset_id": "world_economic_outlook",
                "source_indicator_id": indicator,
                "retrieved_at": retrieved_at,
                "storage_path": str(path),
                "record_count": entry["rows"],
                "checksum_sha256": entry["sha256"],
            }
        )
        with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
            for index, row in enumerate(csv.DictReader(handle)):
                code = (row.get("COUNTRY") or "").strip()
                if code not in classes:
                    raise ValueError(f"undeclared IMF country-dimension code: {code!r}")
                if classes[code] != "economy":
                    continue
                if allowed_iso3 is not None and code not in allowed_iso3:
                    continue
                period = (row.get("TIME_PERIOD") or "").strip()
                raw_value = (row.get("OBS_VALUE") or "").strip()
                if not period or not raw_value:
                    continue
                year = int(period)
                raw_boundary = (row.get("LATEST_ACTUAL_ANNUAL_DATA") or "").strip()
                boundary = normalize_actual_boundary(raw_boundary)
                observation_class = (
                    "actual"
                    if year <= boundary
                    else "estimate"
                    if year <= universe_reference_year
                    else "forecast"
                )
                value = float(raw_value)
                observations.append(
                    {
                        "observation_id": stable_id("obs", "imf_weo", indicator, code, year),
                        "country_id": f"country:{code}",
                        "iso3": code,
                        "reference_period": str(year),
                        "year": year,
                        "metric_id": metric["metric_id"],
                        "value": value,
                        "raw_value": raw_value,
                        "modeled_value": None,
                        "unit": metric["unit"],
                        "frequency": metric["frequency"],
                        "source_id": "imf_weo",
                        "source_dataset_id": "world_economic_outlook",
                        "source_indicator_id": indicator,
                        "source_indicator": indicator,
                        "retrieved_at": retrieved_at,
                        "raw_snapshot_id": raw_snapshot_id,
                        "raw_record_index": index,
                        "transformation_id": metric["transformation"],
                        "pipeline_run_id": run_id,
                        "observation_class": observation_class,
                        "latest_actual_raw": raw_boundary,
                        "latest_actual_year": boundary,
                        "publication_date": manifest["vintage"]["publication_date"],
                        "update_date": manifest["vintage"]["update_date"],
                    }
                )
    return observations, snapshots


def select_weo_universe(
    data: WEOUniverseData, eligibility_path: Path, top_n: int = 50
) -> tuple[list[dict], list[dict]]:
    eligibility = load_eligibility(eligibility_path)
    ranked = sorted(data.observations, key=lambda row: (-row.value, row.iso3))
    selected_rows = ranked[:top_n]
    universe: list[dict] = []
    for rank, row in enumerate(selected_rows, 1):
        if row.iso3 not in eligibility:
            raise ValueError(f"Top-{top_n} WEO economy is not adjudicated: {row.iso3}")
        decision = eligibility[row.iso3]
        if decision["eligibility"] != "eligible":
            raise ValueError(
                f"Top-{top_n} WEO economy is not eligible: {row.iso3} "
                f"({decision['eligibility']})"
            )
        if decision.get("consolidated_into") is not None:
            raise ValueError(
                f"Top-{top_n} WEO economy is consolidated: {row.iso3} -> "
                f"{decision['consolidated_into']}"
            )
        boundary = data.boundaries[row.iso3][1]
        if boundary < row.year:
            raise ValueError(
                f"Top-{top_n} cohort is not fully actual at {row.year}: {row.iso3}"
            )
        universe.append(
            {
                "analytical_entity_id": row.analytical_entity_id,
                "country_id": f"country:{row.iso3}",
                "iso3": row.iso3,
                "name": decision["imf_label"],
                "display_name": "Taiwan" if row.iso3 == "TWN" else decision["imf_label"],
                "gdp_rank": rank,
                "reference_year": row.year,
                "nominal_gdp": row.value,
                "analytical_eligibility": "included",
                "eligibility_basis": decision["eligibility_reason"],
                "consolidated_into": None,
            }
        )
    excluded = [
        {"iso3": row.iso3, "rank": rank, "value": row.value}
        for rank, row in enumerate(ranked[top_n:], top_n + 1)
    ]
    return universe, excluded
