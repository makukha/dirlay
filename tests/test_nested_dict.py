from unittest import TestCase

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Any  # noqa: F401  # used in type hints

from unittest_expander import expand, foreach  # type: ignore

from dirlay.dict import NestedDict


@expand
class TestNestedDict(TestCase):
    # __init__()

    def test_init_empty(self):  # type: () -> None
        self.assertEqual({}, NestedDict())
        self.assertEqual({}, NestedDict(None))
        self.assertEqual({}, NestedDict({}))

    def test_init_invalid(self):  # type: () -> None
        with self.assertRaises(TypeError):
            NestedDict(...)  # type: ignore

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

    @foreach(
        ({}, ('a', 'b'), {'a': 'b'}),
        ({'x': 'y'}, ('a/b', {'c': 'd'}), {'a': {'b': {'c': 'd'}}, 'x': 'y'}),
    )  # type: ignore
    def test_setitem(self, orig, item, expected):  # type: (dict[str, Any], tuple[str, Any], dict[str, Any]) -> None
        x = NestedDict(orig)  # type: NestedDict[dict[str, Any]]
        x[item[0]] = item[1]
        self.assertEqual(expected, x)

    def test_setitem_error(self):  # type: () -> None
        with self.assertRaises(KeyError):
            _ = NestedDict()['missing']

    # __delitem__()

    @foreach(
        ({'a': 'b'}, 'a', {}),
        ({'a': {'b': {'c': 'd'}}, 'x': 'y'}, 'a/b', {'a': {}, 'x': 'y'}),
        ({'a': {'b': {'c': 'd'}}, 'x': 'y'}, 'a', {'x': 'y'}),
    )  # type: ignore
    def test_delitem(self, orig, key, expected):  # type: (dict[str, Any], str, dict[str, Any]) -> None
        x = NestedDict(orig)  # type: NestedDict[dict[str, Any]]
        del x[key]
        self.assertEqual(expected, x)

    def test_delitem_error(self):  # type: () -> None
        with self.assertRaises(KeyError):
            del NestedDict()['missing']
