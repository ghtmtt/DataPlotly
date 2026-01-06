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

update-requirements: $(REQUIREMENS)

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
	@ $(UV_RUN) ruff check --preview  --output-format=concise $(LINT_TARGETS)

lint:: typecheck

lint-fix:
	@ $(UV_RUN) ruff check --preview --fix $(LINT_TARGETS)

format:
	@ $(UV_RUN) ruff format $(LINT_TARGETS)

typecheck:
	@ $(UV_RUN) mypy $(LINT_TARGETS)

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


