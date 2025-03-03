SHELL=/bin/bash -euo pipefail

.PHONY: build
build: dist
dist: src/**/* pyproject.toml README.md uv.lock
	uv lock
	rm -rf $@
	uv build

.PHONY: badges
badges: docs/img/badge/coverage.svg docs/img/badge/tests.svg
docs/img/badge/%.svg: .tmp/%.xml
	mkdir -p $(@D)
	uv run genbadge $* --local -i $< -o $@

.PHONY: requirements
requirements: docs/sphinx/requirements.txt tests/requirements.txt
docs/sphinx/requirements.txt: uv.lock
	uv export --frozen --no-emit-project --only-group sphinx > $@
tests/requirements.txt: uv.lock
	uv export --frozen --no-emit-project --only-group testing > $@

.PHONY: docs
docs: sphinx README.md

.PHONY: sphinx
sphinx: docs/_build
docs/_build: docs/usage.md docs/**/*.* src/**/*.*
	rm -rf $@
	cd docs/sphinx && uv run sphinx-build -b html . _build

README.md: docs/usage.md FORCE
	uv run docsub sync -i $@

%.md: FORCE
	uv run docsub sync -i $@

FORCE:
