SHELL := /bin/bash

.PHONY: setup test lint fmt verify run demo doctor

setup:
	python -m pip install -r requirements.txt
	PIP_NO_BUILD_ISOLATION=1 python -m pip install -e . --no-build-isolation

test:
	pytest -q

lint:
	bash scripts/lint.sh

fmt:
	if command -v black >/dev/null 2>&1; then black src tests; else echo "black not installed"; fi

verify:
	bash scripts/verify.sh

run:
	PYTHONPATH=src python -m netflix_recommender.run_pipeline

demo:
	bash scripts/demo.sh

doctor:
	bash scripts/doctor.sh
