SHELL:=bash

PYTHON_MODULE=DataPlotly

-include .localconfig.mk

REQUIREMENTS_GROUPS= \
	dev \
	tests \
	lint \
	packaging \
	$(NULL)

.PHONY: update-requirements

REQUIREMENTS=$(patsubst %, requirements/%.txt, $(REQUIREMENTS_GROUPS))

update-requirements: $(REQUIREMENTS)

requirements/%.txt: uv.lock
	@echo "Updating requirements for '$*'"; \
	uv export --format requirements.txt \
		--no-annotate \
		--no-editable \
		--no-hashes \
		--only-group $* \
		-q -o $@

#
# Static analysis
#

LINT_TARGETS=$(PYTHON_MODULE) tests $(EXTRA_LINT_TARGETS)

lint::
	@ruff check --preview  --output-format=concise $(LINT_TARGETS)

lint:: typecheck

lint-fix:
	@ruff check --preview --fix $(LINT_TARGETS)

format:
	@ruff format $(LINT_TARGETS)

typecheck:
	@mypy $(LINT_TARGETS)

#
# Tests
#

test:
	@ rm -rf tests/__output__
	@ $(UV_RUN) pytest -v tests


#
# Coverage
#

# Run tests coverage
covtest:
	@ $(UV_RUN) coverage run -m pytest tests/

coverage: covtest
	@echo "Building coverage report"
	@ $(UV_RUN) coverage html

#
# Tests using docker image
#
QGIS_IMAGE_REPOSITORY ?=qgis/qgis
QGIS_IMAGE_TAG ?= $(QGIS_IMAGE_REPOSITORY):$(QGIS_VERSION)

export QGIS_VERSION
export QGIS_IMAGE_TAG
export UID=$(shell id -u)
export GID=$(shell id -g)
docker-test:
	cd .docker && docker compose up \
		--quiet-pull \
		--abort-on-container-exit \
		--exit-code-from qgis
	cd .docker && docker compose down -v
