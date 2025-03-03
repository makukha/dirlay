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
>>> layout = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
>>> layout.data == {'a': {'b': {'c.txt': 'ccc'}, 'd.txt': 'ddd'}}
True
>>> layout['a/b/c.txt']
<Node 'a/b/c.txt': 'ccc'>
>>> 'z.txt' in layout
False
```

Content of files and directories can be updated:

```pycon
>>> layout |= {'a/d.txt': {'e.txt': 'eee'}}
>>> layout['a/b/c.txt'].data *= 2
>>> layout.root()
<Node '.': {'a': {...}}>
>>> layout.data == {'a': {'b': {'c.txt': 'cccccc'}, 'd.txt': {'e.txt': 'eee'}}}
True
```

Instantiate on the file system (in temporary directory by default) and remove when
exiting the context.

```pycon
>>> with layout.mktree():
...     assert getcwd() != layout.basedir  # cwd not changed
...     str(layout['a/b/c.txt'].path.read_text())
'cccccc'
```

Optionally, change current working directory to a layout subdir, and change back
after context manager is exited.

```pycon
>>> with layout.mktree(chdir='a/b'):
...     assert getcwd() == layout.basedir / 'a/b'
...     str(Path('c.txt').read_text())
'cccccc'
```

<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py 'Usage.*' -->
## Create directory layout tree

Directory layout can be constructed from dict:

```pycon
>>> layout = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
>>> layout.basedir is None
True
>>> layout.mktree()
<Dir '/tmp/...': {'a': ...}>
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
>>> layout = Dir({'a/b/c.txt': 'ccc'})
>>> layout.mktree()
<Dir '/tmp/...': {'a': {'b': {'c.txt': 'ccc'}}}>
>>> getcwd()
PosixPath('/tmp')
```

On first `chdir`, initial working directory is stored internally, and will be
restored on `destroy`. Without argument, `chdir` sets current directory to
`layout.basedir`.

```pycon
>>> layout.basedir
PosixPath('/tmp/...')
>>> layout.chdir()
>>> getcwd()
PosixPath('/tmp/...')
```

If `chdir` has argument, it must be a path relative to `basedir`.

```pycon
>>> layout.chdir('a/b')
>>> getcwd()
PosixPath('/tmp/.../a/b')
```

When directory is removed, current directory is restored:

```pycon
>>> layout.rmtree()
>>> getcwd()
PosixPath('/tmp')
```

## Print as tree

```pycon
>>> layout = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
>>> layout.print_rich()
📂 .
└── 📂 a
    ├── 📂 b
    │   └── 📄 c.txt
    └── 📄 d.txt
```

Display `basedir` path and file content:

```pycon
>>> layout.mktree()
<Dir '/tmp/...': ...>
>>> layout.print_rich(real_basedir=True, show_data=True)
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
>>> layout.print_rich(show_data=True, hide_root=True)
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

>>> layout.rmtree()
```

<!-- docsub: end -->
