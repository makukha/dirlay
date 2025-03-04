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
