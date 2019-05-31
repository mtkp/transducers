.PHONY: format check test

test: check
	python -m unittest tests
check:
	mypy **/*.py
format:
	black **/*.py
clean:
	rm -rf .mypy_cache
	rm -rf transducers/__pycache__
	rm -rf tests/__pycache__

