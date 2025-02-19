import sys
from unittest import TestCase, skipUnless

from dirlay import DirLayout
from dirlay.optional import pathlib

Path = pathlib.Path


class TestConstructor(TestCase):
    def test_no_args(self):  # type: () -> None
        layout = DirLayout()
        self.assertEqual({}, layout.to_dict())

    def test_one_level(self):  # type: () -> None
        layout = DirLayout({'a': 'a', 'b': {}})
        self.assertEqual({'a': 'a', 'b': {}}, layout.to_dict())

    def test_deep_path(self):  # type: () -> None
        layout = DirLayout({'a/b/c/d.txt': 'd'})
        self.assertEqual({'a': {'b': {'c': {'d.txt': 'd'}}}}, layout.to_dict())

    def test_deep_nesting(self):  # type: () -> None
        layout = DirLayout({'a': {'b': {'c': {'d.txt': 'd'}}}})
        self.assertEqual({'a': {'b': {'c': {'d.txt': 'd'}}}}, layout.to_dict())

    def test_path_key(self):  # type: () -> None
        layout = DirLayout({'a/b/c': {'d.txt': 'd'}})
        self.assertEqual({'a': {'b': {'c': {'d.txt': 'd'}}}}, layout.to_dict())

    def test_fork(self):  # type: () -> None
        layout = DirLayout({'a/b/c.txt': 'c', 'a/bb.txt': 'bb'})
        self.assertEqual({'a': {'b': {'c.txt': 'c'}, 'bb.txt': 'bb'}}, layout.to_dict())

    # existing subdirectory

    def test_explicit_subdir_before(self):  # type: () -> None
        layout = DirLayout({'a/b': {}, 'a/b/c.txt': 'c'})
        self.assertEqual({'a': {'b': {'c.txt': 'c'}}}, layout.to_dict())

    def test_explicit_subdir_after(self):  # type: () -> None
        layout = DirLayout({'a/b/c.txt': 'c', 'a/b': {}})
        self.assertEqual({'a': {'b': {'c.txt': 'c'}}}, layout.to_dict())

    # pathlib.Path

    @skipUnless(sys.version_info >= (3, 4), 'pathlib not available')
    def test_pathlib(self):  # type: () -> None
        layout = DirLayout({Path('a/b/c.txt'): 'c', Path('d'): {}})
        self.assertEqual({'a': {'b': {'c.txt': 'c'}}, 'd': {}}, layout.to_dict())
