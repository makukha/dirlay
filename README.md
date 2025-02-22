# dirlay
<!-- docsub: begin -->
<!-- docsub: include docs/desc.md -->
> *Directory layout object for testing and documentation*
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: include docs/badges.md -->
[![license](https://img.shields.io/github/license/makukha/dirlay.svg)](https://github.com/makukha/dirlay/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/dirlay.svg#v0.2.1)](https://pypi.python.org/pypi/dirlay)
[![python versions](https://img.shields.io/pypi/pyversions/dirlay.svg)](https://pypi.org/project/dirlay)
[![tests](https://raw.githubusercontent.com/makukha/dirlay/v0.2.1/docs/_meta/badge-tests.svg)](https://github.com/makukha/dirlay)
[![coverage](https://raw.githubusercontent.com/makukha/dirlay/v0.2.1/docs/_meta/badge-coverage.svg)](https://github.com/makukha/dirlay)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![uses docsub](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/makukha/docsub/refs/heads/main/docs/badge/v1.json)](https://github.com/makukha/docsub)
[![mypy](https://img.shields.io/badge/type_checked-mypy-%231674b1)](http://mypy.readthedocs.io)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/ruff)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
<!-- docsub: end -->


<!-- docsub: begin -->
<!-- docsub: include docs/features.md -->
# Features

- Create and remove directory tree with files
- Chdir to layout subdirectories
- Display as rich tree for docs
- Syntactic sugar: mapping interface, context manager, append with `|` and `|=`
- Uses [pathlib2](https://github.com/jazzband/pathlib2) for Python 2
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
* [TL;DR](#tl-dr)
* [Create directory layout tree](#create-directory-layout-tree)
* [Chdir to subdirectory](#chdir-to-subdirectory)
* [Print as tree](#print-as-tree)
<!-- docsub: end -->

```pycon
>>> from dirlay import DirectoryLayout, to_tree
```

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py 'Usage.*' -->
## TL;DR

```pycon
>>> layout = DirLayout() | {'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}}
>>> layout['a/b/c.txt']
PosixPath('a/b/c.txt')
>>> 'z.txt' in layout
False
```

Instantiate on the file system (in temporary directory by default) and remove when
exiting the context.

```pycon
>>> with layout:
...     layout.mktree()
...     str(layout['a/b/c.txt'].read_text())
'ccc'
```

Optionally, change current working directory to a layout subdir, and change back
after context manager is exited.

```pycon
>>> with layout:
...     layout.mktree()
...     layout.chdir('a/b')
...     str(Path('c.txt').read_text())
'ccc'
```

## Create directory layout tree

Directory layout can be constructed from dict:

```pycon
>>> layout = DirLayout({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
>>> layout.basedir is None
True
>>> layout.mktree()
>>> layout.basedir
PosixPath('/tmp/...')
```

And remove when not needed anymore:

```pycon
>>> layout.rmtree()
```

## Chdir to subdirectory

```pycon
>>> import os
>>> os.chdir('/tmp')
```

When layout is instantiated, current directory remains unchanged:

```pycon
>>> layout = DirLayout() | {'a': {'b/c.txt': 'ccc'}}
>>> layout.mktree()
>>> layout.getcwd()
PosixPath('/tmp')
```

On first `chdir`, initial working directory is stored internally, and will be
restored on `rmtree`. Without argument, `chdir` sets current directory to
`layout.basedir`.

```pycon
>>> layout.basedir
PosixPath('/tmp/...')
>>> layout.chdir()
>>> layout.getcwd()
PosixPath('/tmp/...')
```

If `chdir` has argument, it must be a path relative to `basedir`.

```pycon
>>> layout.chdir('a/b')
>>> layout.getcwd()
PosixPath('/tmp/.../a/b')
```

When directory is removed, current directory is restored:

```pycon
>>> layout.rmtree()
>>> layout.getcwd()
PosixPath('/tmp')
```

## Print as tree

```pycon
>>> layout = DirLayout({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
>>> layout.print_tree()
📂 .
└── 📂 a
    ├── 📂 b
    │   └── 📄 c.txt
    └── 📄 d.txt
```

Display `basedir` path and file contents:

```pycon
>>> layout.mktree()
>>> layout.print_tree(real_basedir=True, show_content=True)
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

Extra keyword aguments will be passed through to `rich.tree.Tree`:

```pycon
>>> layout.print_tree(real_basedir=True, show_content=True, hide_root=True)
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
```

<!-- docsub: end -->
<!-- docsub: end #usage.md -->


# See also

* [API Reference](https://dirlay.readthedocs.io/en/latest/api.html)
* [Project Documentation](https://dirlay.readthedocs.io/en/latest)
* [Project Changelog](https://github.com/makukha/dirlay/tree/main/CHANGELOG.md)
