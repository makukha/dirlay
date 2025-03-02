from unittest import TestCase

from dirlay.nested_dict import NestedDict


class TestNestedDict(TestCase):
    # __init__()

    def test_init_empty(self):  # type: () -> None
        self.assertEqual({}, NestedDict())
        self.assertEqual({}, NestedDict(None))
        self.assertEqual({}, NestedDict({}))

    def test_init_invalid(self):  # type: () -> None
        with self.assertRaises(TypeError):
            NestedDict('invalid')  # type: ignore

    def test_init_nested(self):  # type: () -> None
        self.assertEqual({'a': {'b': 'c'}}, NestedDict({'a': {'b': 'c'}}))
        self.assertEqual({'a': {'b': 'c'}}, NestedDict({'a/b': 'c'}))
        self.assertEqual(
            {'a': {'b': 'c', 'd': 'e', 'f': {'g': 'h'}}},
            NestedDict({'a/b': 'c', 'a/d': 'e', 'a/f/g': 'h'}),
        )

    # __eq__()

    # note: positive __eq__() cases are tested all around

    def test_not_equal(self):  # type: () -> None
        self.assertNotEqual({'a': 'b'}, NestedDict({'a': 'c'}))
        self.assertNotEqual((), NestedDict({'a': 'c'}))

    # __len__()

    def test_len(self):  # type: () -> None
        self.assertEqual(0, len(NestedDict({})))
        self.assertEqual(1, len(NestedDict({'a': 'b'})))
        self.assertEqual(2, len(NestedDict({'a': {'b': 'c'}})))
        self.assertEqual(5, len(NestedDict({'a/b/c/d/e': 'f'})))
        self.assertEqual(4, len(NestedDict({'a/b/c': 'd', 'a/b/e': 'f'})))

    # __getitem__()

    def test_getitem(self):  # type: () -> None
        self.assertEqual('b', NestedDict({'a': 'b'})['a'])
        self.assertEqual({'c': 'd'}, NestedDict({'a/b/c': 'd'})['a/b'])

    def test_getitem_error(self):  # type: () -> None
        with self.assertRaises(KeyError):
            _ = NestedDict()['missing']

    # __setitem__()

    def test_setitem(self):  # type: () -> None
        for src, item, expected in (
            ({}, ('a', 'b'), {'a': 'b'}),
            ({'x': 'y'}, ('a/b', {'c': 'd'}), {'a': {'b': {'c': 'd'}}, 'x': 'y'}),
        ):
            result = NestedDict(src)  # type: ignore
            result[item[0]] = item[1]
            self.assertEqual(expected, result)

    def test_setitem_error(self):  # type: () -> None
        with self.assertRaises(KeyError):
            _ = NestedDict()['missing']

    # __delitem__()

    def test_delitem(self):  # type: () -> None
        for src, key, expected in (
            ({'a': 'b'}, 'a', {}),
            ({'a': {'b': {'c': 'd'}}, 'x': 'y'}, 'a/b', {'a': {}, 'x': 'y'}),
            ({'a': {'b': {'c': 'd'}}, 'x': 'y'}, 'a', {'x': 'y'}),
        ):
            result = NestedDict(src)  # type: ignore
            del result[key]
            self.assertEqual(expected, result)

    def test_delitem_error(self):  # type: () -> None
        with self.assertRaises(KeyError):
            del NestedDict()['missing']

    # __contains__()

    def test_contains(self):  # type: () -> None
        for src, key, expected in (
            ({}, 'whatever', False),
            ({'a': 'b'}, 'a', True),
            ({'a': {'b': {'c': 'd'}}}, 'a/b/c', True),
            # invalid use
            ({'a': 'b'}, 0, False),
            ({'a': 'b'}, {}, False),
        ):
            self.assertEqual(expected, key in NestedDict(src))

    # update()

    def test_update(self):  # type: () -> None
        for src, upd, expected in (
            ({}, {'a': 'b'}, {'a': 'b'}),
            ({'a/b': 'c'}, {'a/d': 'e'}, {'a': {'b': 'c', 'd': 'e'}}),
            ({'a/b': 'c'}, {'a': {'d': 'e'}}, {'a': {'b': 'c', 'd': 'e'}}),
        ):
            self.assertEqual(expected, (NestedDict(src) | upd).data)
