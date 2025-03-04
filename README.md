# dirlay
<!-- docsub: begin -->
<!-- docsub: exec yq '"> " + .project.description' pyproject.toml -->
> Directory layout object for testing and documentation
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: include docs/badges.md -->
[![license](https://img.shields.io/github/license/makukha/dirlay.svg)](https://github.com/makukha/dirlay/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/dirlay.svg#v0.4.0)](https://pypi.org/project/dirlay)
[![python versions](https://img.shields.io/pypi/pyversions/dirlay.svg)](https://pypi.org/project/dirlay)
[![tests](https://raw.githubusercontent.com/makukha/dirlay/v0.4.0/docs/img/badge/tests.svg)](https://github.com/makukha/dirlay)
[![coverage](https://raw.githubusercontent.com/makukha/dirlay/v0.4.0/docs/img/badge/coverage.svg)](https://github.com/makukha/dirlay)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![uses docsub](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/makukha/docsub/refs/heads/main/docs/badge/v1.json)](https://github.com/makukha/docsub)
[![mypy](https://img.shields.io/badge/type_checked-mypy-%231674b1)](http://mypy.readthedocs.io)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/ruff)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
<!-- docsub: end -->


<!-- docsub: begin -->
<!-- docsub: include docs/features.md -->
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
<!-- docsub: end -->


# Installation

```shell
$ pip install dirlay[rich]
```


# Usage

<!-- docsub: begin #usage.md -->
<!-- docsub: include docs/usage.md -->
<!-- docsub: begin -->
<!-- docsub: x toc tests/test_usage.py 'Usage.*' -->
* [Create directory layout tree](#create-directory-layout-tree)
* [Chdir to subdirectory](#chdir-to-subdirectory)
* [Print as tree](#print-as-tree)
<!-- docsub: end -->

```pycon
>>> from dirlay import Dir
```

<!-- docsub: begin -->
<!-- docsub: x cases --no-title tests/test_usage.py 'QuickStart' -->
Define directory structure and files content:

```pycon
>>> tree = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
>>> tree.data == {'a': {'b': {'c.txt': 'ccc'}, 'd.txt': 'ddd'}}
True
>>> tree / 'a/b/c.txt'
PosixPath('a/b/c.txt')
>>> tree['a/b/c.txt']
<Node 'a/b/c.txt': 'ccc'>
>>> 'z.txt' in tree
False
```

Content of files and directories can be updated:

```pycon
>>> tree |= {'a/d.txt': {'e.txt': 'eee'}}
>>> tree['a/b/c.txt'].data *= 2
>>> tree.root()
<Node '.': {'a': {...}}>
>>> tree.data == {'a': {'b': {'c.txt': 'cccccc'}, 'd.txt': {'e.txt': 'eee'}}}
True
```

Instantiate on the file system (in temporary directory by default) and remove when
exiting the context.

```pycon
>>> with tree.mktree():
...     assert getcwd() != tree.basedir  # cwd not changed
...     str(tree['a/b/c.txt'].abspath.read_text())
'cccccc'
```

Optionally, change current working directory to a layout subdir, and change back
after context manager is exited.

```pycon
>>> with tree.mktree(chdir='a/b'):
...     assert getcwd() == tree.basedir / 'a/b'
...     str(Path('c.txt').read_text())
'cccccc'
```

<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py 'Usage.*' -->
## Create directory layout tree

Directory layout can be constructed from dict:

```pycon
>>> tree = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
>>> tree.basedir is None
True
>>> tree.mktree()
<Dir '/tmp/...': {'a': ...}>
>>> tree.basedir
PosixPath('/tmp/...')
```

And remove when not needed anymore:

```pycon
>>> tree.rmtree()
```

## Chdir to subdirectory

```pycon
>>> import os
>>> os.chdir('/tmp')
```

When layout is instantiated, current directory remains unchanged:

```pycon
>>> tree = Dir({'a/b/c.txt': 'ccc'})
>>> tree.mktree()
<Dir '/tmp/...': {'a': {'b': {'c.txt': 'ccc'}}}>
>>> getcwd()
PosixPath('/tmp')
```

On first `chdir`, initial working directory is stored internally, and will be
restored on `destroy`. Without argument, `chdir` sets current directory to
`tree.basedir`.

```pycon
>>> tree.basedir
PosixPath('/tmp/...')
>>> tree.chdir()
>>> getcwd()
PosixPath('/tmp/...')
```

If `chdir` has argument, it must be a path relative to `basedir`.

```pycon
>>> tree.chdir('a/b')
>>> getcwd()
PosixPath('/tmp/.../a/b')
```

When directory is removed, current directory is restored:

```pycon
>>> tree.rmtree()
>>> getcwd()
PosixPath('/tmp')
```

## Print as tree

```pycon
>>> tree = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
>>> tree.print_rich()
📂 .
└── 📂 a
    ├── 📂 b
    │   └── 📄 c.txt
    └── 📄 d.txt
```

Display `basedir` path and file content:

```pycon
>>> tree.mktree()
<Dir '/tmp/...': ...>
>>> tree.print_rich(real_basedir=True, show_data=True)
📂 /tmp/...
└── 📂 a
    ├── 📂 b
    │   └── 📄 c.txt
    │       ╭─────╮
    │       │ ccc │
    │       ╰─────╯
    └── 📄 d.txt
        ╭─────╮
        │ ddd │
        ╰─────╯
```

Extra keyword arguments will be passed through to `rich.tree.Tree`:

```pycon
>>> tree.print_rich(show_data=True, hide_root=True)
📂 a
├── 📂 b
│   └── 📄 c.txt
│       ╭─────╮
│       │ ccc │
│       ╰─────╯
└── 📄 d.txt
    ╭─────╮
    │ ddd │
    ╰─────╯

>>> tree.rmtree()
```

<!-- docsub: end -->
<!-- docsub: end #usage.md -->


# See also

* [Documentation](https://dirlay.readthedocs.io)
* [Changelog](https://github.com/makukha/dirlay/tree/main/CHANGELOG.md)
* [Issues](https://github.com/makukha/dirlay/issues)
* [License](https://github.com/makukha/dirlay/tree/main/LICENSE)
