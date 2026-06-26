.PHONY: help install test dry-run validate doctor clean

help:
	@echo "Targets:"
	@echo "  install   Install package in editable mode"
	@echo "  test      Run unit tests"
	@echo "  dry-run   Generate local dry-run review pack"
	@echo "  validate  Validate generated dry-run review pack"
	@echo "  doctor    Inspect local readiness"
	@echo "  clean     Remove generated dry-run output"

install:
	python -m pip install -e .

test:
	python -m unittest discover -s tests -v

dry-run:
	private-ai init --dry-run --mode local-developer --project-name private-ai-demo --company-name local --output-dir generated/dry-run --force

validate:
	private-ai validate generated/dry-run

doctor:
	private-ai doctor

clean:
	python -c "import shutil; shutil.rmtree('generated/dry-run', ignore_errors=True)"

