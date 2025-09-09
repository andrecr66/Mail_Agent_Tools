.PHONY: check lint types test brand-validate brand-init
check: lint types test
lint:
	ruff check --fix .
	ruff format .
types:
	mypy --strict .
test:
	pytest -q --cov=app --cov-report=term-missing
brand-validate:
	python cli.py brand-validate default
brand-init:
	python cli.py brand-init newbrand
