from unittest import TestCase

from dirlay import Dir, Path


class TestGetPath(TestCase):
    def test_get_path(self):  # type: () -> None
        tree = Dir({'a/b': {}})

        # request relative on unlinked
        self.assertEqual(Path('a/b'), tree / 'a/b')
        self.assertEqual(Path('a/b'), tree / Path('a/b'))

        # request absolute on unlinked
        with self.assertRaises(
            RuntimeError, msg='Directory tree must be linked to filesystem'
        ):
            tree // 'a/b'
        with self.assertRaises(
            RuntimeError, msg='Directory tree must be linked to filesystem'
        ):
            tree // Path('a/b')

        with tree.mktree():
            # request relative on linked
            self.assertEqual(Path('a/b'), tree / 'a/b')
            self.assertEqual(Path('a/b'), tree / Path('a/b'))

            # request absolute on linked
            assert tree.basedir is not None
            self.assertEqual(tree['a/b'].abspath, tree // 'a/b')
            self.assertEqual(tree['a/b'].abspath, tree // Path('a/b'))

    def test_error_get_path_absolute(self):  # type: () -> None
        tree = Dir({'a': {}})

        # request relative
        with self.assertRaises(ValueError, msg='Absolute path not allowed'):
            tree / '/a'
        with self.assertRaises(ValueError, msg='Absolute path not allowed'):
            tree / Path('/a')

        # request absolute
        with tree.mktree():
            assert tree.basedir is not None
            with self.assertRaises(ValueError, msg='Absolute path not allowed'):
                tree // str(tree['a'].abspath)
            with self.assertRaises(ValueError, msg='Absolute path not allowed'):
                tree // tree['a'].abspath

    def test_error_get_path_missing(self):  # type: () -> None
        tree = Dir({'a': {}})

        # request relative
        with self.assertRaises(KeyError):
            tree / 'z'
        with self.assertRaises(KeyError):
            tree / Path('z')

        # request absolute
        with tree.mktree():
            assert tree.basedir is not None
            with self.assertRaises(KeyError):
                tree // 'z'
            with self.assertRaises(KeyError):
                tree // Path('z')
