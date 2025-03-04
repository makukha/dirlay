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

    >>> tree = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
    >>> tree.data == {'a': {'b': {'c.txt': 'ccc'}, 'd.txt': 'ddd'}}
    True
    >>> tree / 'a/b/c.txt'
    PosixPath('a/b/c.txt')
    >>> tree['a/b/c.txt']
    <Node 'a/b/c.txt': 'ccc'>
    >>> 'z.txt' in tree
    False

    Content of files and directories can be updated:

    >>> tree |= {'a/d.txt': {'e.txt': 'eee'}}
    >>> tree['a/b/c.txt'].data *= 2
    >>> tree.root()
    <Node '.': {'a': {...}}>
    >>> tree.data == {'a': {'b': {'c.txt': 'cccccc'}, 'd.txt': {'e.txt': 'eee'}}}
    True

    Instantiate on the file system (in temporary directory by default) and remove when
    exiting the context.

    >>> with tree.mktree():
    ...     assert getcwd() != tree.basedir  # cwd not changed
    ...     str(tree['a/b/c.txt'].abspath.read_text())
    'cccccc'

    Optionally, change current working directory to a layout subdir, and change back
    after context manager is exited.

    >>> with tree.mktree(chdir='a/b'):
    ...     assert getcwd() == tree.basedir / 'a/b'
    ...     str(Path('c.txt').read_text())
    'cccccc'
    """


@case
class UsageCreate(TestCase):
    """
    Create directory layout tree

    Directory layout can be constructed from dict:

    >>> tree = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
    >>> tree.basedir is None
    True
    >>> tree.mktree()
    <Dir '/tmp/...': {'a': ...}>
    >>> tree.basedir
    PosixPath('/tmp/...')

    And remove when not needed anymore:

    >>> tree.rmtree()
    """


@case
class UsageChdir(TestCase):
    """
    Chdir to subdirectory

    >>> import os
    >>> os.chdir('/tmp')

    When layout is instantiated, current directory remains unchanged:

    >>> tree = Dir({'a/b/c.txt': 'ccc'})
    >>> tree.mktree()
    <Dir '/tmp/...': {'a': {'b': {'c.txt': 'ccc'}}}>
    >>> getcwd()
    PosixPath('/tmp')

    On first `chdir`, initial working directory is stored internally, and will be
    restored on `destroy`. Without argument, `chdir` sets current directory to
    `tree.basedir`.

    >>> tree.basedir
    PosixPath('/tmp/...')
    >>> tree.chdir()
    >>> getcwd()
    PosixPath('/tmp/...')

    If `chdir` has argument, it must be a path relative to `basedir`.

    >>> tree.chdir('a/b')
    >>> getcwd()
    PosixPath('/tmp/.../a/b')

    When directory is removed, current directory is restored:

    >>> tree.rmtree()
    >>> getcwd()
    PosixPath('/tmp')
    """


@skipIf(sys.version_info < (3, 6), 'rich not supported')
@case
class UsageTree(TestCase):
    """
    Print as tree

    >>> tree = Dir({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
    >>> tree.print_rich()
    📂 .
    └── 📂 a
        ├── 📂 b
        │   └── 📄 c.txt
        └── 📄 d.txt

    Display `basedir` path and file content:

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

    Extra keyword arguments will be passed through to `rich.tree.Tree`:

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
    """
