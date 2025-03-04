from typing import Any

try:
    from rich.tree import Tree  # type: ignore[import-not-found,unused-ignore]
except ImportError:
    Tree = None  # type: ignore[assignment,misc]  # assign to type

from dirlay import Dir

def as_rich_tree(
    tree: Dir,
    real_basedir: bool = ...,
    show_data: bool = ...,
    **kwargs: Any,
) -> Tree: ...
