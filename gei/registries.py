from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .config import ROOT

SOURCE_REGISTRY_PATH = ROOT / "config" / "sources.json"
TRANSFORMATION_REGISTRY_PATH = ROOT / "config" / "transformations.json"
COUNTRY_REGISTRY_PATH = ROOT / "config" / "countries.json"
ANALYTICAL_ENTITY_REGISTRY_PATH = ROOT / "config" / "analytical_entities.json"


def load_versioned_registry(path: Path, collection: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("schema_version"), str) or not isinstance(payload.get(collection), list):
        raise ValueError(f"Malformed {collection} registry")
    return payload


def registry_version(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def validate_registries(metrics: list[dict], sources: list[dict], transformations: list[dict]) -> list[str]:
    errors: list[str] = []
    source_ids = [row.get("source_id") for row in sources]
    transform_ids = [row.get("transformation_id") for row in transformations]
    for label, values in (("source", source_ids), ("transformation", transform_ids)):
        duplicates = sorted({value for value in values if value and values.count(value) > 1})
        if duplicates: errors.append(f"duplicate {label} IDs: {duplicates}")
    supported_formats = {"currency", "percent", "ratio", "integer", "decimal", "number", "signed_percent", "basis_points"}
    supported_frequencies = {"annual", "quarterly", "monthly", "daily"}
    categories = {row.get("category") for row in metrics if row.get("category")}
    for metric in metrics:
        if metric.get("source_id") not in source_ids: errors.append(f"unknown source ID for {metric.get('metric_id')}")
        if metric.get("transformation") not in transform_ids: errors.append(f"unknown transformation for {metric.get('metric_id')}")
        if metric.get("formatting") not in supported_formats: errors.append(f"invalid format for {metric.get('metric_id')}")
        if metric.get("frequency") not in supported_frequencies: errors.append(f"unsupported frequency for {metric.get('metric_id')}")
        if not isinstance(metric.get("unit"), str) or not metric["unit"].strip(): errors.append(f"malformed unit for {metric.get('metric_id')}")
        if metric.get("category") not in categories: errors.append(f"invalid category for {metric.get('metric_id')}")
        if not isinstance(metric.get("indexing_allowed"), bool): errors.append(f"missing indexing policy for {metric.get('metric_id')}")
        if metric.get("change_transformation") not in {"cagr", "percent_change", "percentage_point_change"}: errors.append(f"invalid change transformation for {metric.get('metric_id')}")
        if not isinstance(metric.get("change_windows"), list) or not all(isinstance(value, int) and value > 0 for value in metric.get("change_windows", [])): errors.append(f"invalid change windows for {metric.get('metric_id')}")
    return errors


def write_country_registry(countries: list[dict], path: Path = COUNTRY_REGISTRY_PATH) -> dict:
    rows = [{"country_id": row["country_id"], "iso2": row["iso2"], "iso3": row["iso3"], "canonical_name": row["name"], "short_name": row["name"], "region": row.get("region"), "subregion": None, "income_group": row.get("income_group"), "currency_code": None, "world_bank_code": row["iso3"], "imf_code": None, "ilo_code": None, "oecd_code": None, "un_code": None, "status": "source_active", "territory_classification": None} for row in sorted(countries, key=lambda item: item["iso3"])]
    payload = {"schema_version":"1.0","authority":"World Bank country dimension; no sovereignty classification added","countries":rows}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    return payload


def validate_country_registry(payload: dict) -> list[str]:
    errors=[]; rows=payload.get("countries",[])
    for field in ("country_id","iso2","iso3"):
        values=[row.get(field) for row in rows]
        duplicates=sorted({value for value in values if value and values.count(value)>1})
        if duplicates: errors.append(f"duplicate {field}: {duplicates}")
    for row in rows:
        if not isinstance(row.get("iso3"),str) or len(row["iso3"])!=3 or not row["iso3"].isupper(): errors.append(f"invalid ISO3: {row.get('iso3')}")
        if not isinstance(row.get("iso2"),str) or len(row["iso2"])!=2 or not row["iso2"].isupper(): errors.append(f"invalid ISO2: {row.get('iso2')}")
        if not row.get("world_bank_code"): errors.append(f"missing World Bank mapping: {row.get('country_id')}")
    return errors


def validate_analytical_entity_registry(payload: dict) -> list[str]:
    errors: list[str] = []; rows = payload.get("entities", [])
    required = {"analytical_entity_id", "display_name", "analytical_eligibility", "eligibility_policy_version", "eligibility_basis", "effective_from", "review_owner", "authoritative_ids", "source_references"}
    if not isinstance(payload.get("eligibility_policy_version"), str): errors.append("missing eligibility policy version")
    ids = [row.get("analytical_entity_id") for row in rows]
    if len(ids) != len(set(ids)): errors.append("duplicate analytical entity IDs")
    for row in rows:
        missing = sorted(required - row.keys())
        if missing: errors.append(f"missing entity fields for {row.get('analytical_entity_id')}: {missing}")
        if row.get("analytical_eligibility") not in {"included", "excluded", "pending_review"}: errors.append(f"invalid eligibility for {row.get('analytical_entity_id')}")
        if row.get("eligibility_policy_version") != payload.get("eligibility_policy_version"): errors.append(f"entity policy mismatch for {row.get('analytical_entity_id')}")
        if not isinstance(row.get("authoritative_ids"), dict) or not any(row.get("authoritative_ids", {}).values()): errors.append(f"missing authoritative identifier for {row.get('analytical_entity_id')}")
        if not isinstance(row.get("source_references"), list) or not row.get("source_references"): errors.append(f"missing source references for {row.get('analytical_entity_id')}")
    return errors
