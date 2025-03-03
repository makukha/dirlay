import os
from unittest import TestCase
from uuid import uuid4

from dirlay import Dir, getcwd


class TestFilesystem(TestCase):
    def assertFilesystem(self, layout):  # type: (Dir) -> None
        assert layout.basedir is not None
        for node in layout.leaves():
            self.assertTrue(node.path.exists())
            if not node.is_dir:
                self.assertEqual(node.data, node.path.read_text())

    # test mktree/rmtree

    def test_error_remove_not_instantiated(self):  # type: () -> None
        with self.assertRaises(RuntimeError):
            Dir({'c.md': 'c'}).rmtree()

    def test_create_remove_tempdir(self):  # type: () -> None
        layout = Dir({'a': {'b': {'c.md': 'C'}}})
        # instantiate in temporary directory
        layout.mktree()
        assert layout.basedir is not None
        self.assertFilesystem(layout)
        # remove
        basedir = layout.basedir
        layout.rmtree()
        self.assertFalse(basedir.exists())

    def test_create_remove_userdir(self):  # type: () -> None
        layout = Dir({'a': {'b': {'c.md': 'C'}}})
        # instantiate in directory provided by user
        os.chdir('/tmp')
        layout.mktree(uuid4().hex)
        assert layout.basedir is not None
        self.assertFilesystem(layout)
        # remove
        basedir = layout.basedir
        layout.rmtree()
        self.assertFalse(basedir.exists())

    # test chdir

    def test_error_chdir_not_instantiated(self):  # type: () -> None
        with self.assertRaises(RuntimeError):
            Dir({'c.md': 'C'}).chdir('.')

    def test_error_chdir_absolute(self):  # type: () -> None
        layout = Dir({'c.md': 'C'})
        with self.assertRaises(RuntimeError):
            layout.chdir(getcwd())

    def test_chdir(self):  # type: () -> None
        layout = Dir({'a': {'b': {'c.md': 'C'}}})
        layout.mktree()
        assert layout.basedir is not None
        cwd = getcwd()
        layout.chdir('.')
        self.assertEqual(layout.basedir, getcwd())
        layout.chdir('a')
        self.assertEqual(layout.basedir / 'a', getcwd())
        layout.chdir('a/b')
        self.assertEqual(layout.basedir / 'a/b', getcwd())
        layout.rmtree()  # original cwd is restored on rmtree()
        self.assertEqual(cwd, getcwd())
