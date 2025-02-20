import os
from unittest import TestCase
from uuid import uuid4

from dirlay import DirLayout


class TestFilesystem(TestCase):
    def assertFilesystem(self, layout):  # type: (DirLayout) -> None
        assert layout.basedir is not None  # type hint
        for path, value in layout:
            path = layout.basedir / path
            self.assertTrue(path.exists())
            if value is not None:
                with open(str(path), 'rt') as f:
                    self.assertEqual(value, f.read())

    def test_remove_not_instantiated(self):  # type: () -> None
        with self.assertRaises(RuntimeError):
            DirLayout({'c.txt': 'c'}).rmtree()

    def test_create_remove_tempdir(self):  # type: () -> None
        layout = DirLayout({'a': {'b': {'c.txt': 'c'}}})
        # instantiate in temporary directory
        layout.mktree()
        assert layout.basedir is not None  # type hint
        self.assertFilesystem(layout)
        # remove
        basedir = layout.basedir
        layout.rmtree()
        self.assertFalse(basedir.exists())

    def test_create_remove_userdir(self):  # type: () -> None
        layout = DirLayout({'a': {'b': {'c.txt': 'c'}}})
        # instantiate in directory provided by user
        os.chdir('/tmp')
        layout.mktree(uuid4().hex)
        assert layout.basedir is not None  # type hint
        self.assertFilesystem(layout)
        # remove
        basedir = layout.basedir
        layout.rmtree()
        self.assertFalse(basedir.exists())

    def test_chdir_not_instantiated(self):  # type: () -> None
        with self.assertRaises(RuntimeError):
            DirLayout({'c.txt': 'c'}).chdir('.')

    def test_chdir_absolute(self):  # type: () -> None
        layout = DirLayout({'c.txt': 'c'})
        with self.assertRaises(RuntimeError):
            layout.chdir(os.getcwd())

    def test_chdir(self):  # type: () -> None
        layout = DirLayout({'a': {'b': {'c.txt': 'c'}}})
        layout.mktree()
        assert layout.basedir is not None  # type hint
        cwd = os.getcwd()
        layout.chdir('.')
        self.assertEqual(layout.basedir, layout.getcwd())
        layout.chdir('a')
        self.assertEqual(layout.basedir / 'a', layout.getcwd())
        layout.chdir('a/b')
        self.assertEqual(layout.basedir / 'a/b', layout.getcwd())
        layout.rmtree()  # original cwd is restored on rmtree()
        self.assertEqual(cwd, os.getcwd())
