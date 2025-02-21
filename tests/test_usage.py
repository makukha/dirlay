# encoding: utf-8
from doctest import ELLIPSIS
import sys
from unittest import TestCase, skipIf

from doctestcase import doctestcase

from dirlay import DirLayout


case = doctestcase(globals={'DirLayout': DirLayout}, options=ELLIPSIS)


@case
class UsageCreate(TestCase):
    """
    Create directory layout tree

    >>> layout = DirLayout({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
    >>> layout.basedir is None
    True
    >>> layout.mktree()
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

    >>> layout = DirLayout({'a': {'b/c.txt': 'ccc'}})
    >>> layout.mktree()
    >>> layout.getcwd()
    PosixPath('/tmp')

    On first `chdir`, initial working directory is stored internally, and will be
    restored on `rmtree`. Without argument, `chdir` sets current directory to
    `layout.basedir`.

    >>> layout.basedir
    PosixPath('/tmp/...')
    >>> layout.chdir()
    >>> layout.getcwd()
    PosixPath('/tmp/...')

    If `chdir` has argument, it must be a path relative to `basedir`.

    >>> layout.chdir('a/b')
    >>> layout.getcwd()
    PosixPath('/tmp/.../a/b')

    When directory is removed, current directory is restored:

    >>> layout.rmtree()
    >>> layout.getcwd()
    PosixPath('/tmp')
    """


@skipIf(sys.version_info < (3, 6), 'rich not supported')
@case
class UsageTree(TestCase):
    """
    Print as tree

    >>> layout = DirLayout({'a': {'b/c.txt': 'ccc', 'd.txt': 'ddd'}})
    >>> layout.print_tree()
    📂 .
    └── 📂 a
        ├── 📂 b
        │   └── 📄 c.txt
        └── 📄 d.txt

    Display `basedir` path and file contents:

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

    Extra keyword aguments will be passed through to `rich.tree.Tree`:

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
    """
