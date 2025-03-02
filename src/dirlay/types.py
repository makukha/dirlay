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

if sys.version_info < (3, 9):
    AnyDict = Union[StrDict, UserDict]  # type: TypeAlias
else:
    AnyDict = Union[StrDict, UserDict[str, Any]]  # type: TypeAlias

# node tree

if sys.version_info < (3, 9):
    NodeTree = Mapping  # type: TypeAlias
else:
    NodeTree = Mapping[str, 'NodeValue']  # type: TypeAlias

NodeValue = Union[NodeTree, str]  # type: TypeAlias
