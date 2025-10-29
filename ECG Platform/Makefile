.PHONY: help install install-dev clean test lint format docker-build docker-up docs benchmark

help:
	@echo "ECG2Signal Development Commands"
	@echo "================================"
	@echo "install          - Install package and dependencies"
	@echo "install-dev      - Install with development dependencies"
	@echo "clean            - Remove build artifacts and cache"
	@echo "test             - Run test suite"
	@echo "test-cov         - Run tests with coverage report"
	@echo "lint             - Run linters (ruff, mypy)"
	@echo "format           - Format code with black and isort"
	@echo "docker-build     - Build Docker image"
	@echo "docker-up        - Start Docker services"
	@echo "docker-down      - Stop Docker services"
	@echo "docs             - Build documentation"
	@echo "benchmark        - Run performance benchmarks"
	@echo "download-models  - Download pre-trained models"
	@echo "export-onnx      - Export models to ONNX format"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,training]"
	pre-commit install

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=ecg2signal --cov-report=html --cov-report=term

lint:
	ruff check ecg2signal/ tests/
	mypy ecg2signal/

format:
	black ecg2signal/ tests/
	isort ecg2signal/ tests/
	ruff check --fix ecg2signal/ tests/

docker-build:
	docker build -t ecg2signal:latest -f docker/Dockerfile .

docker-up:
	docker-compose -f docker/compose.yaml up -d

docker-down:
	docker-compose -f docker/compose.yaml down

docs:
	cd docs && mkdocs build

benchmark:
	bash scripts/benchmark.sh

download-models:
	bash scripts/download_demo_models.sh

export-onnx:
	python scripts/export_onnx.py --all

run-api:
	uvicorn ecg2signal.api.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	streamlit run ecg2signal/ui/app.py

convert:
	ecg2signal convert $(FILE) --output $(OUTPUT)
