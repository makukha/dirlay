import os
from unittest import TestCase
from uuid import uuid4

from dirlay import Dir, Path, getcwd


class TestFilesystem(TestCase):
    def assertFilesystem(self, tree):  # type: (Dir) -> None
        assert tree.basedir is not None
        for node in tree.leaves():
            self.assertTrue(node.abspath.exists())
            if not node.isdir:
                self.assertEqual(node.data, node.abspath.read_text())

    # test mktree/rmtree

    def test_error_remove_not_instantiated(self):  # type: () -> None
        with self.assertRaises(RuntimeError):
            Dir({'c.md': 'c'}).rmtree()

    def test_create_remove_tempdir(self):  # type: () -> None
        tree = Dir({'a': {'b': {'c.md': 'C'}}})
        # instantiate in temporary directory
        tree.mktree()
        assert tree.basedir is not None
        self.assertFilesystem(tree)
        # remove
        basedir = tree.basedir
        tree.rmtree()
        self.assertFalse(basedir.exists())

    def test_create_remove_userdir(self):  # type: () -> None
        tree = Dir({'a': {'b': {'c.md': 'C'}}})
        # instantiate in directory provided by user
        os.chdir('/tmp')
        tree.mktree(uuid4().hex)
        assert tree.basedir is not None
        self.assertFilesystem(tree)
        # remove
        basedir = tree.basedir
        tree.rmtree()
        self.assertFalse(basedir.exists())

    # test chdir

    def test_error_chdir_not_instantiated(self):  # type: () -> None
        with self.assertRaises(RuntimeError):
            Dir({'c.md': 'C'}).chdir('.')

    def test_error_chdir_absolute(self):  # type: () -> None
        tree = Dir({'c.md': 'C'})
        with self.assertRaises(RuntimeError):
            tree.chdir(getcwd())

    def test_chdir(self):  # type: () -> None
        tree = Dir({'a': {'b': {'c.md': 'C'}}})
        tree.mktree()
        assert tree.basedir is not None
        cwd = getcwd()
        tree.chdir('.')
        self.assertEqual(tree.basedir, getcwd())
        tree.chdir('a')
        self.assertEqual(tree.basedir / 'a', getcwd())
        tree.chdir('a/b')
        self.assertEqual(tree.basedir / 'a/b', getcwd())
        tree.rmtree()  # original cwd is restored on rmtree()
        self.assertEqual(cwd, getcwd())

    def test_mktree_chdir(self):  # type: () -> None
        cwd = getcwd()

        # default
        with Dir().mktree() as tree:
            self.assertEqual(cwd, getcwd())  # not changed

        # None
        with Dir().mktree(chdir=None) as tree:
            self.assertEqual(cwd, getcwd())  # not changed

        # False
        with Dir().mktree(chdir=False):
            self.assertEqual(cwd, getcwd())  # not changed

        # True
        with Dir().mktree(chdir=True) as tree:
            self.assertEqual(tree.basedir, getcwd())  # changed to basedir

        # root: str
        with Dir().mktree(chdir='.') as tree:
            self.assertEqual(tree.basedir, getcwd())  # changed to basedir

        # root: Path
        with Dir().mktree(chdir=Path()) as tree:
            self.assertEqual(tree.basedir, getcwd())  # changed to basedir

        # subdir: str
        with Dir({'a': {}}).mktree(chdir='a') as tree:
            self.assertEqual(tree.basedir / 'a', getcwd())  # type: ignore[operator]

        # subdir: Path
        with Dir({'a': {}}).mktree(chdir=Path('a')) as tree:
            self.assertEqual(tree.basedir / 'a', getcwd())  # type: ignore[operator]

        # subsubdir: str
        with Dir({'a': {'b': {}}}).mktree(chdir='a/b') as tree:
            self.assertEqual(tree.basedir / 'a/b', getcwd())  # type: ignore[operator]

        # subsubdir: Path
        with Dir({'a': {'b': {}}}).mktree(chdir=Path('a/b')) as tree:
            self.assertEqual(tree.basedir / 'a/b', getcwd())  # type: ignore[operator]

        # errors

        # not found
        with self.assertRaises(OSError):
            with Dir() as tree:
                tree.mktree(chdir='x')

        # invalid type
        with self.assertRaises(TypeError):
            with Dir() as tree:
                tree.mktree(chdir=[])  # type: ignore

        # absolute: str
        with self.assertRaises(ValueError):
            with Dir() as tree:
                tree.mktree(chdir='/tmp')

        # absolute: Path
        with self.assertRaises(ValueError):
            with Dir() as tree:
                tree.mktree(chdir=Path('/tmp'))
