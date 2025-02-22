from typing import Any

try:
    from rich.tree import Tree  # type: ignore[import-not-found,unused-ignore]
except ImportError:
    Tree = None  # type: ignore[assignment,misc]  # assign to type

from dirlay import DirLayout

def to_tree(
    layout: DirLayout,
    real_basedir: bool = ...,
    show_content: bool = ...,
    **kwargs: Any,
) -> Tree: ...
