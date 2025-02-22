# Changelog

All notable changes to this project will be documented in this file based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- See upcoming changes in [News directory](https://github.com/makukha/dirlay/tree/main/NEWS.d)

<!-- scriv-insert-here -->

<a id='changelog-0.2.1'></a>
## [0.2.1](https://github.com/makukha/dirlay/releases/tag/v0.2.1) — 2025-02-22

***Added 🌿***

- New methods to append entries: `__or__()`, `__ior__()`, `add()`, `update()`
- New method `copy()` to get a deep copy
- Method `__contains__()` to check whether directory layout object contains specific path
- Item access with `__getitem__()` returning `Path` object
- Context manager protocol `__enter__()` and `__exit__()` that calls `rmtree()` if `mktree()` was called earlier

<a id='changelog-0.2.0'></a>
## [0.2.0](https://github.com/makukha/dirlay/releases/tag/v0.2.0) — 2025-02-21

***Breaking 🔥***

- Renamed argument `show_basedir` to `real_basedir`

***Added 🌿***

- Optional `kwargs` to `DirLayout.print_tree` and `to_tree`

<a id='changelog-0.1.0'></a>
## [0.1.0](https://github.com/makukha/dirlay/releases/tag/v0.1.0) — 2025-02-20

***Added 🌿***

- Initial release
