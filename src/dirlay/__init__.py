import os
import shutil
import sys
from tempfile import mkdtemp

try:
    from reprlib import aRepr

    a_repr = aRepr.repr
except ImportError:  # pragma: no cover
    a_repr = repr

from dirlay.__version__ import __version__ as __version__
from dirlay.nested_dict import NestedDict as BaseNestedDict
from dirlay.optional import pathlib, rich

if sys.version_info > (3,):
    NestedDict = BaseNestedDict
else:  # pragma: no cover
    from collections import OrderedDict as BaseOrderedDict

    class OrderedDict(BaseOrderedDict):
        def __eq__(self, other):
            return dict(self) == dict(other)

        def __repr__(self):
            return '{{{}}}'.format(
                ', '.join('{!r}: {!r}'.format(k, v) for k, v in self.items())
            )

    class NestedDict(BaseNestedDict):
        dict_class = OrderedDict


if rich is not None:
    from dirlay.format_rich import as_rich_tree, rich_print
else:  # pragma: no cover
    as_rich_tree = None

    def rich_print(*args):
        pass


__all__ = [
    'Dir',
    'NestedDict',
    'Node',
    'Path',
    'getcwd',
]

Path = pathlib.Path


class Node(object):
    """
    Node proxy object representing directory or file.

    Attributes:

        key (``str``):
            String path relative to `~dirlay.Dir` root, and also a mapping key:

            >>> tree = Dir({'a': {'b.md': 'B'}})
            >>> tree[tree['a/b.md'].key] == tree['a/b.md']
            True

        data (``str | dict[str, str | dict]``):
            In-memory file content if the node is a file, or, if `~dirlay.Node.isdir`
            is ``True``, a dictionary, representing directory structure.

        abspath (`~pathlib.Path` | ``None``):
            Absolute node path, if directory layout is linked to the filesystem,
            or ``None`` otherwise.

        relpath (`~pathlib.Path`):
            Node path relative to `~dirlay.Dir.basedir` of parent `~dirlay.Dir`;
            corresponds to `~dirlay.Node.key`

        isdir (``bool``):
            Whether the node is a directory.
    """

    def __init__(self, key, base, basedir):
        self.key = key
        self.relpath = Path(key)
        self.abspath = basedir / key if basedir is not None else None
        self._base = base
        self._name = '.' if key == '.' else self.relpath.name

    def __eq__(self, other):
        return (
            isinstance(other, Node)
            and self.key == other.key
            and self.abspath == other.abspath
            and self._base is other._base
        )

    @property
    def data(self):
        return self._base[self._name]

    @data.setter
    def data(self, value):
        self._base[self._name] = value

    @property
    def isdir(self):
        return isinstance(self.data, NestedDict.dict_class)

    def __repr__(self):
        return '<Node {!r}: {}>'.format(str(self.key), a_repr(self.data))


class Dir:
    """
    Directory layout class. See :ref:`Use cases` for examples.
    """

    def __init__(self, entries=None):
        r"""
        Example:

            >>> from dirlay import Dir

            >>> Dir({'docs/index.rst': '', 'src': {}, 'pyproject.toml': '\n'}).data
            {'docs': {'index.rst': ''}, 'src': {}, 'pyproject.toml': '\n'}

            >>> Dir({'a/b/c/d/e/f.txt': '', 'a/b/c/d/ee': {}}).data
            {'a': {'b': {'c': {'d': {'e': {'f.txt': ''}, 'ee': {}}}}}}
        """  # fmt: skip

        self._tree = NestedDict()
        if entries is not None:
            self.update(entries)
        self._basedir = None
        self._basedir_remove = False
        self._original_cwd = None

    def __repr__(self):
        return '<Dir {!r}: {}>'.format(
            str(self._basedir or '.'),
            a_repr(self._tree.data),
        )

    @property
    def data(self):
        """
        Internal data mapping.
        """
        return self._tree.data

    def __contains__(self, path):
        """
        Check whether directory layout object contains path defined.
        """
        return norm(path) in self._tree

    def __eq__(self, other):
        """
        Two directory layouts are equal if they have:

        - equal files and directories (both path and data)
        - equal `~dirlay.Dir.basedir`
        """
        return (
            isinstance(other, Dir)
            and self.basedir == other.basedir
            and self._tree == other._tree
        )

    def __getitem__(self, path):
        """
        Return `~dirlay.Node` object from string path.
        """
        key = norm(path)
        if os.path.isabs(key):
            raise ValueError('Absolute path not allowed: {!r}'.format(path))
        base, name = self._tree.traverse(key)
        if name not in base:
            raise KeyError(key)
        return Node(key, base=base, basedir=self.basedir)

    def __floordiv__(self, path):
        """
        Return absolute `~pathlib.Path` object for sub-path; equivalent to
        ``tree[path].abspath``.

        Directory layout must be linked to the file system.
        """
        self._require_linked_to_filesystem()
        return self.__getitem__(path).abspath

    def __truediv__(self, path):
        """
        Return relative `~pathlib.Path` object; equivalent to ``tree[path].relpath``.
        """
        return self.__getitem__(path).relpath

    __div__ = __truediv__  # Python 2 compatibility

    def __iter__(self):
        """
        Iterate over tuples of path and value.
        """
        for k, _ in self._tree.items():
            yield k

    def items(self):
        """
        Iterate over tuples of ``str`` and  `~dirlay.Node` objects relative to
        layout root.
        """
        for k in self._tree.keys():
            parent, _ = self._tree.traverse(k)
            yield k, Node(k, base=parent, basedir=self.basedir)

    def keys(self):
        """
        Get all string paths relative to layout root.
        """
        return self._tree.keys()

    def values(self):
        """
        Get all `~dirlay.Node` objects relative to layout root.
        """
        return tuple(v for _, v in self.items())

    def root(self):
        """
        Get root `~dirlay.Node` object.
        """
        return Node('.', base={'.': self._tree.data}, basedir=self.basedir)

    def leaves(self):
        """
        Get all `~dirlay.Node` objects representing files or empty directories.
        """
        return tuple(n for n in self.values() if not n.isdir or n.data == {})

    def __or__(self, entries):
        """
        Append dict of entries to a copy of self.

        Equivalent to ``x = self.copy(); x.update(entries)``.
        """
        ret = self.copy()
        ret.update(entries)
        return ret

    def __ior__(self, entries):
        """
        Append dict of entries to self.

        Equivalent to ``self.update(entries)``.
        """
        self.update(entries)
        return self

    def __enter__(self):
        """
        Enter context manager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager.
        """
        if self.basedir is not None:
            self.rmtree()

    def update(self, entries):
        """
        Update or add entries from dictionary.
        """
        self._tree.update(entries)

    def copy(self):
        """
        Return a deep copy of self.
        """
        return Dir(self._tree.data)

    # filesystem operations

    @property
    def basedir(self):
        """
        Base filesystem directory as `~pathlib.Path` object.

        When ``None``, directory layout object is not instantiated (not created on the
        file system).
        """
        return None if self._basedir is None else self._basedir

    def mktree(self, basedir=None, chdir=None):
        """
        Create directories and files in given or temporary directory.

        Args:

            basedir (`~pathlib.Path` | ``str`` | ``None``, optional):
                Path to base directory under which directories and files will be
                created; if ``None`` (default), temporary directory is used. After the
                directory structure is created, ``basedir`` value is available as
                `~dirlay.Dir.basedir` attribute.

            chdir (`~pathlib.Path` | ``str`` | ``bool`` | ``None``, optional):
                Change the current directory to given path. If ``None`` (default) or
                ``False``, directory is not changed; ``True`` is equivalent to ``'.'``.

        Returns:

            ``None``

        Raises:

            FileExistsError: If ``basedir`` path already exists.
        """
        # prepare
        if basedir is None:
            self._basedir = Path(mkdtemp())
            self._basedir_remove = True
        else:
            basedir = Path(basedir)
            if not basedir.exists():
                basedir.mkdir(parents=True, exist_ok=True)
                self._basedir_remove = True
            self._basedir = basedir.resolve()
        # create
        for node in self.leaves():
            if node.isdir:
                node.abspath.mkdir(parents=True, exist_ok=True)
            else:
                node.abspath.parent.mkdir(parents=True, exist_ok=True)
                if sys.version_info > (3,):
                    node.abspath.write_text(node.data)
                else:  # pragma: no cover
                    node.abspath.write_text(node.data.decode('utf-8'))
        # chdir
        if chdir not in (None, False):
            self.chdir('.' if chdir is True else chdir)
        #
        return self

    def rmtree(self):
        """
        Remove directory and all its contents.

        If ``basedir`` was created, it will be removed. If ``chdir`` argument
        was passed, current working directory will be restored to the original one.

        Returns:

            ``None``
        """
        self._require_linked_to_filesystem()
        # chdir back if needed
        if self._original_cwd is not None:
            os.chdir(str(self._original_cwd))
            self._original_cwd = None
        # remove basedir if needed
        if self._basedir_remove:
            if self._basedir.exists():
                shutil.rmtree(str(self._basedir))
            self._basedir_remove = False
        self._basedir = None

    # current directory operations

    def chdir(self, path=None):
        """
        Change current directory to a subdirectory relative to layout base.

        Args:

            path (`~pathlib.Path` | ``str`` | ``None``):
                Relative path to subdirectory to be chdir'ed to; if ``None`` (default),
                `~dirlay.Dir.basedir` will be used.

        Returns:

            ``None``

        Raises:

            ValueError: If ``path`` is absolute.
        """
        # validate type
        self._require_linked_to_filesystem()
        if path is None:
            path = Path()
        elif isinstance(path, Path) or isinstance(path, str):
            path = Path(path)
        else:
            raise TypeError('Required str or Path object')
        # assert relative
        if path.is_absolute():
            raise ValueError('Absolute path not allowed')
        # chdir
        if self._original_cwd is None:
            self._original_cwd = getcwd()
        os.chdir(str(self.basedir / path))

    # helpers

    def _require_linked_to_filesystem(self):
        if self._basedir is None:
            raise RuntimeError('Directory tree must be linked to filesystem')

    # formatting

    def as_rich(self, real_basedir=False, show_data=False, **kwargs):
        """
        Return :external+rich:py:obj:`~rich.tree.Tree` representation;
        `rich <https://rich.readthedocs.io>`_ must be installed.
        See :ref:`Print as tree` for examples.

        Args:

            real_basedir (``bool``):
                Whether to show real base directory name instead of ``'.'``; defaults to
                ``False``.

            show_data (``bool``):
                Whether to include file content in the box under the file name; defaults
                to ``False``.

            kwargs (``Any``):
                Optional keyword arguments passed to `~rich.tree.Tree`.

        Returns:

            :external+rich:py:obj:`~rich.tree.Tree`
        """
        if rich is None:
            raise NotImplementedError('Optional dependency required: dirlay[rich]')
        return as_rich_tree(
            self, real_basedir=real_basedir, show_data=show_data, **kwargs
        )

    def print_rich(self, real_basedir=False, show_data=False, **kwargs):
        """
        Print :external+rich:py:obj:`~rich.tree.Tree` representation.
        See `~dirlay.Dir.as_rich`.

        Returns:

            ``None``
        """
        if rich is None:
            raise NotImplementedError('Optional dependency required: dirlay[rich]')
        tree = self.as_rich(real_basedir=real_basedir, show_data=show_data, **kwargs)
        rich_print(tree)


# public helpers


def getcwd():
    """
    Get current working directory.

    Works for Python 2 and 3.

    Returns:

        `~pathlib.Path`
    """
    return Path.cwd().resolve()


# internal helpers


def norm(path):
    return os.path.normpath(str(path))
