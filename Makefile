.PHONY: clean-pyc clean-build docs clean docs
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python3.6 -c "$$BROWSER_PYSCRIPT"

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "test-integration - run integration tests"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "coverage-ci - check code coverage and generate cobertura report"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build.d/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -fr .cache/
	rm -f .coverage
	rm -fr htmlcov/
	rm -f test-results.xml

lint:
	flake8 sceptre_migration_tool tests integration-tests
	python3.6 setup.py check -r -s -m

test:
	pytest

test-all:
	tox

test-integration: install
	behave integration-tests/

test-integration-wip: install
	behave -w integration-tests/

coverage-ci:
	coverage erase
	coverage run --source sceptre_migration_tool -m pytest
	coverage html

coverage: coverage-ci
	coverage report --show-missing
	$(BROWSER) htmlcov/index.html

docs:
	rm -f docs/sceptre_migration_tool.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ sceptre_migration_tool
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

docs-api:
	rm -f docs/_api/sceptre_migration_tool.rst
	rm -f docs/_api/modules.rst
	sphinx-apidoc -o docs/_api sceptre_migration_tool
	$(MAKE) -C docs/_api clean
	$(MAKE) -C docs/_api html
	rm -rf docs/docs/api/
	cp -r docs/_api/_build/html docs/docs/
	mv docs/docs/html docs/docs/api

docs-latest: docs-api
	$(MAKE) -C docs build-latest

docs-tag: docs-api
	$(MAKE) -C docs build-tag

docs-dev: docs-api
	$(MAKE) -C docs build-dev

docs-commit: docs-api
	$(MAKE) -C docs build-commit

serve-docs-latest: docs-latest
	$(MAKE) -C docs serve-latest

serve-docs-tag: docs-tag
	$(MAKE) -C docs serve-tag

serve-docs-dev: docs-dev
	$(MAKE) -C docs serve-dev

serve-docs-commit: docs-commit
	$(MAKE) -C docs serve-commit

dist: clean
	python3.6 setup.py sdist
	python3.6 setup.py bdist_wheel build -b build.d
	ls -l dist

install-make-tools:
	pip3.6 install -r make-requirements.txt --user

install: clean
	pip3.6 install .

install-dev: clean
	pip3.6 install -r requirements.txt
	pip3.6 install -e .
	@echo "To install the documentation dependencies, run:\ncd docs\nmake install"
