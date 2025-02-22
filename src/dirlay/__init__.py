import os
import shutil
import sys
from tempfile import mkdtemp

from dirlay.__version__ import __version__
from dirlay.optional import pathlib, rich

if rich is not None:
    import rich
    from dirlay.format_rich import to_tree

    rich_print = getattr(rich, 'print')  # noqa: B009  # Python 2 compatibility
else:
    rich_print = None
    to_tree = None


Path = pathlib.Path

__all__ = [
    '__version__',
    'DirLayout',
    'Path',
]


class DirLayout:
    """
    Directory layout class. See :ref:`Use cases` for examples.
    """

    def __init__(self, entries=None):
        r"""
        Example:

            >>> from dirlay import DirLayout

            >>> DirLayout({
            ...     'docs/index.rst': '',
            ...     'src': {},
            ...     'pyproject.toml': '[project]\n',
            ... }).to_dict()
            {'docs': {'index.rst': ''}, 'pyproject.toml': '[project]\n', 'src': {}}

            >>> DirLayout({
            ...     'a/b/c/d/e/f.txt': '',
            ...     'a/b/c/d/ee': {},
            ... }).to_dict()
            {'a': {'b': {'c': {'d': {'e': {'f.txt': ''}, 'ee': {}}}}}}
        """  # fmt: skip

        self._tree = {}
        if entries is not None:
            self.add(entries)
        self._basedir = None
        self._prevdir = None

    def __contains__(self, path):
        """
        Check whether directory layout object contains path defined.
        """
        ret = self._tree
        for part in Path(path).parts:
            if part not in ret:
                return False
            ret = ret[part]
        return True

    def __eq__(self, other):
        """
        Two directory layouts are equal if they have:

        - equal files and directories (both path and content)
        - equal `~dirlay.DirLayout.basedir`
        """
        return self._basedir == other._basedir and self._tree == other._tree

    def __getitem__(self, path):
        """
        Return `~pathlib.Path` object from string path.
        """
        if path not in self:
            raise KeyError(path)
        return Path(path) if self.basedir is None else self.basedir / path

    def __iter__(self):
        """
        Iterate over tuples of path and value.
        """
        return walk(self._tree)

    def __or__(self, entries):
        """
        Append dict of entries to a copy of self.

        Equivalent to ``self.copy().update(entries)``.
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

    @classmethod
    def _add_path(cls, base_dict, base_path, path, value, exist_ok=False):
        # validate
        base_path = Path('.' if base_path is None else os.path.normpath(str(base_path)))
        path = Path(os.path.normpath(str(path)))
        if base_path.is_absolute():
            raise ValueError('Absolute path not allowed: "{}"'.format(base_path))
        if path.is_absolute():
            raise ValueError('Absolute path not allowed: "{}"'.format(path))

        # prepare
        value = {} if value is None else value

        # drill down path directories
        base = base_dict
        for i, part in enumerate(path.parts[:-1]):
            if part not in base:
                base[part] = {}
            elif not isinstance(base[part], dict):
                partial_path = Path.joinpath(*path.parents[: i + 1])
                msg = 'Path {} is not a directory'.format(Path(base_path, partial_path))
                raise NotADirectoryError(msg)
            base = base[part]

        # add
        if isinstance(value, dict):
            base.setdefault(path.name, {})
            new_base_path = Path(base_path, path.parent)
            for k, v in value.items():
                cls._add_path(base[path.name], new_base_path, k, v, exist_ok=exist_ok)
        elif isinstance(value, str):
            if path.name in base:
                if not exist_ok:
                    msg = 'Path {} already exists'.format(Path(base_path, path))
                    raise FileExistsError(msg)
            base[path.name] = value
        else:
            raise TypeError('Invalid value type {}'.format(type(value)))

    def add(self, entries):
        """
        Add entries from dictionary.
        """
        for k, v in entries.items():
            self._add_path(self._tree, None, k, v, exist_ok=False)
        return self

    def copy(self):
        """
        Return a deep copy of self.
        """
        return DirLayout(self._tree)

    def to_dict(self):
        """
        Return nested `dict` representation of the directory layout.
        """
        ret = {}

        def append_entries(base, entries):  # type: (dict[str, Any], dict[Any, Any]) -> None
            paths = list(entries.keys())
            paths.sort()
            for path in paths:
                k = str(path)
                v = entries[path]
                if isinstance(v, dict):
                    base[k] = {}
                    append_entries(base[k], v)
                else:
                    base[k] = v

        append_entries(ret, self._tree)
        return ret

    def update(self, entries):
        """
        Update or add entries from dictionary.
        """
        for k, v in entries.items():
            self._add_path(self._tree, None, k, v, exist_ok=True)

    # filesystem operations

    @property
    def basedir(self):
        """
        Base filesystem directory as `~pathlib.Path` object.

        When ``None``, directory layout object is not instantiated (not created on the
        file system).
        """
        return None if self._basedir is None else Path(self._basedir)

    def mktree(self, basedir=None):
        """
        Instantiate layout in given or temporary directory.

        Args:
            basedir (`~pathlib.Path` | ``str`` | ``None``):
                path to base directory under which directories and files will be
                created; if ``None`` (default), temporary directory is used. After the
                directory structure is created, ``basedir`` value is available as
                `~dirlay.DirLayout.basedir` attribute.

        Returns:
            `None`

        Raises:
            FileExistsError: if ``basedir`` path already exists.
        """
        # prepare
        if basedir is None:
            self._basedir = Path(mkdtemp())
        else:
            basedir = Path(basedir)
            if basedir.exists():
                raise FileExistsError('Path already exists: {}'.format(basedir))
            basedir.mkdir(parents=True, exist_ok=True)
            self._basedir = basedir.resolve()
        # create
        for path, value in walk(self._tree):
            p = Path(self._basedir, path)
            parent = p if value is None else p.parent
            parent.mkdir(parents=True, exist_ok=True)
            if value is not None:
                if sys.version_info > (3,):
                    p.write_text(value)
                else:
                    p.write_text(value.decode('utf-8'))

    def rmtree(self):
        """
        Remove directory and all its contents.

        Returns:
            ``None``
        """
        self._assert_tree_created()
        # chdir back if needed
        if self._prevdir is not None:
            os.chdir(self._prevdir)
            self._prevdir = None
        # cleanup base if needed
        basedir = str(self._basedir)
        if os.path.exists(basedir):
            shutil.rmtree(basedir)
        self._basedir = None

    # current directory operations

    def chdir(self, path=None):
        """
        Change current directory to a subdirectory relative to layout base.

        Args:
            path (`~pathlib.Path` | ``str`` | ``None``):
                relative path to subdirectory to be chdir'ed to; if ``None`` (default),
                `~dirlay.DirLayout.basedir` will be used.

        Returns:
            `None`

        Raises:
            ValueError: if ``path`` is absolute.
        """
        # validate
        self._assert_tree_created()
        path = Path('.') if path is None else Path(path)
        if path.is_absolute():
            raise ValueError('Absolute path not allowed: "{}"'.format(path))
        # chdir
        if self._prevdir is None:
            self._prevdir = os.getcwd()
        os.chdir(str(self.basedir / path))

    def getcwd(self):
        """
        Get current working directory.

        Returns:
            `~pathlib.Path`
        """
        return Path.cwd().resolve()

    def _assert_tree_created(self):
        if self._basedir is None:
            raise RuntimeError('Directory tree must be created')

    # formatting

    def print_tree(self, real_basedir=False, show_content=False, **kwargs):
        """
        Print as :external+rich:py:obj:`~rich.tree.Tree`. See :ref:`Print as tree`
        for examples.

        Args:
            real_basedir (``bool``):
                whether to show real base directory name instead of ``'.'``; defaults to
                ``False``.
            show_content (``bool``):
                whether to include file content in the box under the file name; defaults to
                ``False``.
            kwargs (``Any``):
                optional keyword arguments passed to `~rich.tree.Tree`.

        Returns:
            ``None``
        """
        if rich is None:
            raise NotImplementedError(
                'Optional dependency rich is required; install as dirlay[rich]'
            )
        tree = to_tree(
            self, real_basedir=real_basedir, show_content=show_content, **kwargs
        )
        rich_print(tree)


# internal helpers


def walk(entries, prefix=None):
    if prefix is None:
        prefix = Path('.')
    for name, v in entries.items():
        if v is None or v == {}:
            yield (Path(prefix, name), None)
        elif isinstance(v, dict):
            next_prefix = Path(prefix, name)
            yield (next_prefix, None)
            for x in walk(v, prefix=next_prefix):  # syntax supported by Python 2
                yield x
        elif isinstance(v, (str, Path)):
            yield (Path(prefix, name), v)
        else:
            raise TypeError('Unexpected item type {}'.format(type(v)))
