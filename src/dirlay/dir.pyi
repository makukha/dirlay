from pathlib import Path
from typing import Any, Iterable, Iterator, Optional, Tuple, Union

from typing_extensions import TypeAlias

PathType: TypeAlias = Union[Path, str]

NodeTree: TypeAlias = dict[PathType, 'NodeValue']
NodeValue: TypeAlias = Union[None, str, dict[PathType, 'NodeValue']]

StrNodeTree: TypeAlias = dict[str, 'StrNodeValue']
StrNodeValue: TypeAlias = Union[None, str, dict[str, 'StrNodeValue']]

class DirLayout:
    _tree: StrNodeTree
    _basedir: Optional[Path]
    _prevdir: Optional[str]
    def __init__(self, entries: Optional[NodeTree] = ...) -> None: ...
    def __eq__(self, other: Any) -> bool: ...
    def __iter__(self) -> Iterator[Tuple[Path, Optional[str]]]: ...
    def to_dict(self) -> StrNodeTree: ...
    @classmethod
    def _add_path(
        cls,
        base_dict: StrNodeTree,
        base_path: Optional[Path],
        path: Path,
        value: NodeValue,
        exist_ok: bool = ...,
    ) -> None: ...
    def _assert_tree_created(self) -> None: ...
    @property
    def basedir(self) -> Optional[Path]: ...
    def chdir(self, path: Optional[PathType] = ...) -> None: ...
    def getcwd(self) -> Path: ...
    def mktree(self, base: Optional[PathType] = ...) -> None: ...
    def rmtree(self) -> None: ...
    def print_tree(
        self,
        real_basedir: bool = ...,
        show_content: bool = ...,
    ) -> None: ...

def walk(
    entries: StrNodeTree,
    prefix: Optional[Path] = ...,
) -> Iterable[Tuple[Path, Optional[str]]]: ...
