from gei.config import load_metric_registry
from gei.registries import ANALYTICAL_ENTITY_REGISTRY_PATH, COUNTRY_REGISTRY_PATH, SOURCE_REGISTRY_PATH, TRANSFORMATION_REGISTRY_PATH, load_versioned_registry, validate_analytical_entity_registry, validate_country_registry, validate_registries
import json


metrics=load_metric_registry();sources=load_versioned_registry(SOURCE_REGISTRY_PATH,"sources")["sources"];transformations=load_versioned_registry(TRANSFORMATION_REGISTRY_PATH,"transformations")["transformations"]
errors=validate_registries(metrics,sources,transformations)
errors.extend(validate_analytical_entity_registry(load_versioned_registry(ANALYTICAL_ENTITY_REGISTRY_PATH,"entities")))
if COUNTRY_REGISTRY_PATH.exists():errors.extend(validate_country_registry(json.loads(COUNTRY_REGISTRY_PATH.read_text())))
if errors:raise SystemExit("\n".join(errors))
print(f"Configuration valid: {len(metrics)} metrics, {len(sources)} sources, {len(transformations)} transformations.")
