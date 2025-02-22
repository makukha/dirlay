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
