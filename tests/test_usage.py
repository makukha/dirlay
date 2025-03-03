# encoding: utf-8
from doctest import ELLIPSIS
import sys
from unittest import TestCase, skipIf

from doctestcase import doctestcase

from dirlay import Dir, Path, getcwd


case = doctestcase(
    globals={'Dir': Dir, 'Path': Path, 'getcwd': getcwd},
    options=ELLIPSIS,
)


@case
class QuickStart(TestCase):
    """
    QuickStart

    Define directory structure and files content:

    >>> layout = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
    >>> layout.data == {'a': {'b': {'c.txt': 'ccc'}, 'd.txt': 'ddd'}}
    True
    >>> layout['a/b/c.txt']
    <Node 'a/b/c.txt': 'ccc'>
    >>> 'z.txt' in layout
    False

    Content of files and directories can be updated:

    >>> layout |= {'a/d.txt': {'e.txt': 'eee'}}
    >>> layout['a/b/c.txt'].data *= 2
    >>> layout.root()
    <Node '.': {'a': {...}}>
    >>> layout.data == {'a': {'b': {'c.txt': 'cccccc'}, 'd.txt': {'e.txt': 'eee'}}}
    True

    Instantiate on the file system (in temporary directory by default) and remove when
    exiting the context.

    >>> with layout.mktree():
    ...     assert getcwd() != layout.basedir  # cwd not changed
    ...     str(layout['a/b/c.txt'].path.read_text())
    'cccccc'

    Optionally, change current working directory to a layout subdir, and change back
    after context manager is exited.

    >>> with layout.mktree(chdir='a/b'):
    ...     assert getcwd() == layout.basedir / 'a/b'
    ...     str(Path('c.txt').read_text())
    'cccccc'
    """


@case
class UsageCreate(TestCase):
    """
    Create directory layout tree

    Directory layout can be constructed from dict:

    >>> layout = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
    >>> layout.basedir is None
    True
    >>> layout.mktree()
    <Dir '/tmp/...': {'a': ...}>
    >>> layout.basedir
    PosixPath('/tmp/...')

    And remove when not needed anymore:

    >>> layout.rmtree()
    """


@case
class UsageChdir(TestCase):
    """
    Chdir to subdirectory

    >>> import os
    >>> os.chdir('/tmp')

    When layout is instantiated, current directory remains unchanged:

    >>> layout = Dir({'a/b/c.txt': 'ccc'})
    >>> layout.mktree()
    <Dir '/tmp/...': {'a': {'b': {'c.txt': 'ccc'}}}>
    >>> getcwd()
    PosixPath('/tmp')

    On first `chdir`, initial working directory is stored internally, and will be
    restored on `destroy`. Without argument, `chdir` sets current directory to
    `layout.basedir`.

    >>> layout.basedir
    PosixPath('/tmp/...')
    >>> layout.chdir()
    >>> getcwd()
    PosixPath('/tmp/...')

    If `chdir` has argument, it must be a path relative to `basedir`.

    >>> layout.chdir('a/b')
    >>> getcwd()
    PosixPath('/tmp/.../a/b')

    When directory is removed, current directory is restored:

    >>> layout.rmtree()
    >>> getcwd()
    PosixPath('/tmp')
    """


@skipIf(sys.version_info < (3, 6), 'rich not supported')
@case
class UsageTree(TestCase):
    """
    Print as tree

    >>> layout = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
    >>> layout.print_rich()
    📂 .
    └── 📂 a
        ├── 📂 b
        │   └── 📄 c.txt
        └── 📄 d.txt

    Display `basedir` path and file content:

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

    Extra keyword arguments will be passed through to `rich.tree.Tree`:

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
    """
