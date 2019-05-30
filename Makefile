.PHONY: format check test
test: check
	python -m tests
check:
	mypy **/*.py
format:
	black **/*.py

