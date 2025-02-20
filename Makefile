SHELL=/bin/bash -euo pipefail

.PHONY: build
build: dist
dist: src/**/* pyproject.toml README.md uv.lock
	uv lock
	rm -rf $@
	uv build

.PHONY: badges
badges: docs/_meta/badge-coverage.svg docs/_meta/badge-tests.svg
docs/_meta/badge-%.svg: .tmp/%.xml
	uv run genbadge $* --local -i $< -o $@

.PHONY: docs
docs: sphinx readthedocs README.md

.PHONY: sphinx
sphinx: docs/sphinx/_build
docs/sphinx/_build: docs/*.md docs/sphinx/*.* src/**/*.*
	rm -rf $@
	cd docs/sphinx && uv run sphinx-build -b html . _build

.PHONY: readthedocs
readthedocs: docs/sphinx/requirements.txt
docs/sphinx/requirements.txt: pyproject.toml uv.lock
	uv export --only-group sphinx --no-emit-project > $@

README.md: docs/usage.md FORCE
	uv run docsub sync -i $@

%.md: FORCE
	uv run docsub sync -i $@

FORCE:
