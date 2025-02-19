import os
import shutil
import sys
from tempfile import mkdtemp

from dirlay.optional import pathlib, rich

if rich is not None:
    import rich
    from dirlay.format_rich import to_tree

    rich_print = getattr(rich, 'print')  # noqa: B009  # Python 2 compatibility
else:
    rich_print = None
    to_tree = None

Path = pathlib.Path


class DirLayout:
    """
    Directory layout class. See :ref:`Use cases` for details.
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
            for k, v in entries.items():
                self._add_path(self._tree, None, k, v, exist_ok=False)
        self._basedir = None
        self._prevdir = None

    def __eq__(self, other):
        return self._basedir == other._basedir and self._tree == other._tree

    def __iter__(self):
        return walk(self._tree)

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

    # filesystem operations

    @property
    def basedir(self):
        """
        Base filesystem directory.
        """
        return None if self._basedir is None else Path(self._basedir)

    def mktree(self, basedir=None):
        """
        Instantiate layout in given or temporary directory.
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
        """
        return Path.cwd().resolve()

    def _assert_tree_created(self):
        if self._basedir is None:
            raise RuntimeError('Directory tree must be created')

    # formatting

    def print_tree(self, show_basedir=False, show_content=False):
        if rich is None:
            raise NotImplementedError(
                'Optional dependency rich is required; install as dirlay[rich]'
            )
        tree = to_tree(self, show_basedir=show_basedir, show_content=show_content)
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
