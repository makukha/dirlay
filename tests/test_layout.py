from unittest import TestCase

from dirlay import Dir

try:
    from typing import List, Tuple  # noqa: F401  # used in type hints
    from dirlay.types import DictNode, StrDict  # noqa: F401  # used in type hints
except ImportError:
    pass


class TestConstruct(TestCase):
    def test_no_args(self):  # type: () -> None
        self.assertEqual({}, Dir().data)

    def test_construct(self):  # type: () -> None
        for src, data in (
            ({'a': 'A', 'b': {}}, {'a': 'A', 'b': {}}),
            ({'a/b/c/d.txt': 'D'}, {'a': {'b': {'c': {'d.txt': 'D'}}}}),
            ({'a': {'b': {'c': {'d.txt': 'D'}}}}, {'a': {'b': {'c': {'d.txt': 'D'}}}}),
            ({'a/b/c': {'d.txt': 'D'}}, {'a': {'b': {'c': {'d.txt': 'D'}}}}),
            ({'a/b/c.txt': 'C', 'a/bb.txt': 'BB'}, {'a': {'b': {'c.txt': 'C'}, 'bb.txt': 'BB'}}),
            ({'a/b': {}, 'a/b/c.txt': 'c'}, {'a': {'b': {'c.txt': 'c'}}}),
            ({'a/b/c.txt': 'c', 'a/b': {}}, {'a': {'b': {'c.txt': 'c'}}}),
            ({'b': {}, 'a': {}}, {'a': {}, 'b': {}}),
        ):  # fmt: skip
            self.assertEqual(data, Dir(src).data)  # type: ignore
            self.assertEqual(data, Dir(Dir(src).data).data)  # type: ignore


class TestModify(TestCase):
    def test_update_other(self):  # type: () -> None
        def assertPassing(src, upd, expected):  # type: (StrDict, StrDict, StrDict) -> None
            result = Dir(src)
            result |= upd
            self.assertEqual(Dir(expected), result)
            self.assertEqual(Dir(expected), Dir(src) | upd)
            self.assertEqual(Dir(expected), Dir(src) | Dir(upd).data)

        for src, upd, expected in (
            ({'a/b.md': 'B'}, {'a/d.md': 'D', 'e.md': 'E'}, {'a': {'b.md': 'B', 'd.md': 'D'}, 'e.md': 'E'}),
            ({'a/b.md': 'B'}, {'a/b.md': 'UPD'}, {'a/b.md': 'UPD'}),
            ({'a/b.md': 'B'}, {'a/b.md': {}}, {'a/b.md': {}}),
        ):  # fmt: skip
            assertPassing(src, upd, expected)

    def test_update_other_error(self):  # type: () -> None
        src = {'a/b.md': 'B'}
        upd = {'a/b.md/c.md': 'C'}
        with self.assertRaises(ValueError):
            Dir(src) | upd

    def test_update_data(self):  # type: () -> None
        def assertPassing(src, kvs, expected):  # type: (StrDict, List[Tuple[str, DictNode]], StrDict) -> None
            updated = Dir(src)
            for k, v in kvs:
                updated[k].data = v
                self.assertEqual(v, updated[k].data)
                self.assertEqual(Dir(expected), updated)

        for src, kvs, expected in (
            ({'a/b.md': 'B'}, [('a/b.md', 'UPD')], {'a/b.md': 'UPD'}),
        ):  # fmt: skip
            assertPassing(src, kvs, expected)  # type: ignore

    def test_update_data_error(self):  # type: () -> None
        def assertError(src, k, v, errtype):  # type: (StrDict, str, DictNode, type[Exception]) -> None
            with self.assertRaises(errtype):
                Dir(src)[k].data = v

        for src, k, v, errtype in (
            ({'a/b.md': 'B'}, 'a/b.md/c.md', 'C', ValueError),
            ({'a/b': {}}, 'a/b/c.md', 'C', KeyError),
        ):
            assertError(src, k, v, errtype)
