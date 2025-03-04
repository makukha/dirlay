# Features

- Create directory tree and files from Python `dict`
- Chdir to tree subdirectories
- Display as rich tree for documentation
- Developer friendly syntax:
  - reference nodes by paths: `tree['a/b.md']`
  - get sub-paths: `tree / 'a/b.md'` (relative), `tree // 'a/b.md'` (absolute)
  - add, update, delete nodes: `tree |= {'d': {}}`, `del tree['a']`
  - create tree under given or temporary directory
  - `contextmanager` interface to unlink tree on exit
- Fully typed
- Python 2 support (using [pathlib2](https://github.com/jazzband/pathlib2))
