PYTHON ?= python3

.PHONY: test check validate-config data data-fixture build app scale inventory audit clean-pyc

test:
	$(PYTHON) -m pytest -q

check:
	python3 -m compileall -q gei tests scripts
	node --check app/app.js
	python3 -m json.tool config/metrics.json >/dev/null
	python3 -m scripts.validate_config

validate-config:
	python3 -m scripts.validate_config

data:
	python3 -m gei.pipeline

data-fixture:
	python3 -m scripts.offline_smoke

build: check
	python3 -m scripts.build_static

app:
	python3 -m http.server 8765 --directory app

scale:
	python3 scripts/scale_test.py

inventory:
	python3 -m scripts.inventory

audit:
	python3 -m scripts.build_audit_bundle

clean-pyc:
	find gei tests scripts -type d -name __pycache__ -prune -exec rm -rf {} +
