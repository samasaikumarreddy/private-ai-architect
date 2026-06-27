.PHONY: help install test architect blueprint-validate dry-run validate ingest evaluate chat doctor clean

help:
	@echo "Targets:"
	@echo "  install   Install package in editable mode"
	@echo "  test      Run unit tests"
	@echo "  architect Generate the sample v0.3 guided architecture pack"
	@echo "  blueprint-validate Validate the generated v0.3 blueprint"
	@echo "  dry-run   Generate local dry-run review pack"
	@echo "  validate  Validate generated dry-run review pack"
	@echo "  ingest    Build local JSON index from sample docs"
	@echo "  evaluate  Run sample retrieval quality cases"
	@echo "  chat      Query local JSON index with cited excerpts"
	@echo "  doctor    Inspect local readiness"
	@echo "  clean     Remove generated dry-run output"

install:
	python -m pip install -e .

test:
	python -m unittest discover -s tests -v

architect:
	private-ai architect --answers-file examples/architect/local-rag-answers.json --output-dir generated/architect --force

blueprint-validate:
	private-ai blueprint validate generated/architect

dry-run:
	private-ai init --dry-run --mode local-developer --project-name private-ai-demo --company-name local --output-dir generated/dry-run --force

validate:
	private-ai validate generated/dry-run

ingest:
	private-ai ingest examples/sample-company-docs --collection docs --output-dir generated/index --force

evaluate:
	private-ai evaluate --index generated/index/index.json --cases examples/evaluation/local-rag-cases.json

chat:
	private-ai chat "AI usage rules" --index generated/index/index.json

doctor:
	private-ai doctor

clean:
	python -c "import shutil; shutil.rmtree('generated/architect', ignore_errors=True)"
	python -c "import shutil; shutil.rmtree('generated/dry-run', ignore_errors=True)"
	python -c "import shutil; shutil.rmtree('generated/index', ignore_errors=True)"
