from unittest import TestCase

from dirlay import DirLayout


class TestAsDict(TestCase):
    def test_ordering(self):  # type: () -> None
        layout = DirLayout({'b': {}, 'a': {}})
        self.assertEqual({'a': {}, 'b': {}}, layout.to_dict())
