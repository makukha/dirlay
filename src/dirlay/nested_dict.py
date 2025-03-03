try:
    from collections import UserDict
except ImportError:  # pragma: no cover

    class UserDict(object):
        pass


class NestedDict(UserDict):
    """
    General purpose dict that allows accessing nested items by delimited keys.
    """

    dict_class = dict
    sep = '/'

    def __init__(self, dict=None, **kwargs):
        self.data = self.dict_class()
        self._len = 0
        self.update(dict, **kwargs)

    def __eq__(self, other):
        try:
            return self.data == self._operand(other)
        except TypeError:
            return False

    def __len__(self):
        return self._len

    def __getitem__(self, key):
        parent, lastpart = self._traverse(key, create_parents=False, base=self.data)
        return parent[lastpart]

    def __setitem__(self, key, item):
        self._update({key: item}, base=self.data)

    def __delitem__(self, key):
        parent, lastpart = self._traverse(key, create_parents=False, base=self.data)
        self._len -= self._count(parent[lastpart])
        del parent[lastpart]

    def _count(self, item):
        if not isinstance(item, self.dict_class):
            return 1
        else:
            return 1 + sum(self._count(v) for v in item.values())

    def traverse(self, key):
        return self._traverse(key, create_parents=False, base=self.data)

    def _traverse(self, key, create_parents, base):
        parent = base
        prev, last = None, -1
        while last < len(key):
            # find next delimited part
            prev = last + 1
            last = key.find(self.sep, prev)
            if last == -1:
                return parent, key[prev:]
            part = key[prev:last]
            # traverse nested
            if part not in parent:
                if create_parents:
                    parent[part] = self.dict_class()
                    self._len += 1
                else:
                    raise KeyError(key[:last])
            parent = parent[part]
            if not isinstance(parent, dict):
                raise ValueError('Not a dictionary: {}'.format(key[:last]))

    def update(self, other=None, **kwargs):  # type: ignore[override]
        if other:
            self._update(self._operand(other), base=self.data)
        self._update(kwargs, base=self.data)

    def _update(self, other, base):
        for k in other.keys():
            v = other[k]
            parent, key = self._traverse(k, create_parents=True, base=base)
            if key not in parent:
                self._len += 1
            if isinstance(v, dict) or isinstance(v, self.dict_class):
                if key not in parent or not isinstance(parent[key], self.dict_class):
                    parent[key] = self.dict_class()
                self._update(v, base=parent[key])
            else:
                parent[key] = v

    def __iter__(self):
        for k, _, _ in self._walk(self.data, prefix=None):
            yield k

    def items(self):
        return ((k, v) for (k, v, _) in self._walk(self.data, prefix=None))

    def keys(self):
        return tuple(k for (k, _, _) in self._walk(self.data, prefix=None))

    def values(self):
        return tuple(v for (_, v, _) in self._walk(self.data, prefix=None))

    def _walk(self, entries, prefix=None):
        for key, item in entries.items():
            nested_key = key if prefix is None else self.sep.join((prefix, key))
            yield nested_key, item, entries
            if isinstance(item, self.dict_class):
                for kvp in self._walk(item, prefix=nested_key):  # Python 2 support
                    yield kvp

    def __contains__(self, key):
        if not isinstance(key, str):
            return False
        try:
            parent, name = self._traverse(key, create_parents=False, base=self.data)
            return name in parent
        except (KeyError, ValueError):
            return False

    def get(self, key, default=None):
        try:
            parent, lastpart = self._traverse(key, create_parents=False, base=self.data)
        except (KeyError, ValueError):
            return default
        else:
            return parent.get(lastpart, default)

    def __repr__(self):
        return repr(self.data)

    def __or__(self, other):
        ret = self.copy()
        ret.update(self._operand(other))
        return ret

    def __ror__(self, other):
        ret = self.__class__(self._operand(other))
        ret.update(self)
        return ret

    def __ior__(self, other):
        self.update(self._operand(other))
        return self

    @staticmethod
    def _operand(other):
        if isinstance(other, UserDict):
            return other.data
        elif isinstance(other, dict):
            return other
        else:
            raise TypeError('Not a dictionary type: {}'.format(type(other)))

    def __copy__(self):
        return self.__class__(self.data)

    def clear(self):
        self.data.clear()

    def copy(self):
        return self.__copy__()

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d
