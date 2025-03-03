from collections import UserDict
from collections.abc import Mapping
import sys
from typing import Any as Any, Dict as Dict, Union as Union

from typing_extensions import TypeAlias  # noqa: F401  # used in type hints

from dirlay.optional import pathlib


Path = pathlib.Path  # type: TypeAlias
PathType = Union[Path, str]  # type: TypeAlias

# dicts

StrDict = Dict[str, Any]  # type: TypeAlias

if sys.version_info < (3, 9):  # pragma: no cover
    AnyDict = Union[StrDict, UserDict]  # type: TypeAlias
else:
    AnyDict = Union[StrDict, UserDict[str, Any]]  # type: TypeAlias

# node tree

if sys.version_info < (3, 9):  # pragma: no cover
    DictTree = Mapping  # type: TypeAlias
else:
    DictTree = Mapping[str, 'DictNode']  # type: TypeAlias
    """
    TypeAlias: User representation of directory structure to be provided as input
    to `~dirlay.Dir` constructor or `~dirlay.Dir.update` method and operations:

    >>> tree = Dir({'a': {'b.md': 'b file content'}})
    >>> tree |= {'c.md': 'c file content'}
    """

DictNode = Union[str, DictTree]  # type: TypeAlias
"""
TypeAlias: User representation of directory node — a file or a directory.
"""
