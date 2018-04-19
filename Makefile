module = smalldataviewer
version_file = $(module)/version.py
current_version := $(shell grep -Po "\d+\.\d+\.\d+" $(version_file))

install:
	pip install .

install-full:
	pip install .[full]

install-dev:
	pip install -r requirements.txt && pip install -e .[full]

test:
	pytest

test-all:
	tox

clean: clean-build clean-pyc clean-test

clean-build: ## remove build artifacts
	rm -f MANIFEST
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -rf .pytest_cache
	rm -rf .tox

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

version-patch:
	bumpversion --current-version $(current_version) patch $(module)/version.py --commit --tag

version-minor:
	bumpversion --current-version $(current_version) minor $(module)/version.py --commit --tag

version-major:
	bumpversion --current-version $(current_version) major $(module)/version.py --commit --tag

release: dist ## package and upload a release
	twine upload dist/*
