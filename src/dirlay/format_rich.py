try:
    from typing import TYPE_CHECKING
except ImportError:  # pragma: no cover
    TYPE_CHECKING = False

if TYPE_CHECKING:  # pragma: no cover
    from typing import Optional  # noqa: F401  # used in type hint comment

from rich import print as rich_print  # noqa: F401  # rich_print is exported
from rich.box import ROUNDED
from rich.panel import Panel
from rich.tree import Tree

try:
    from rich.console import Group
except ImportError:  # pragma: no cover
    from rich.group import Group

from .optional import pathlib


Path = pathlib.Path


class DefaultTheme:
    style = 'tree'  # type: str
    guide_style = 'tree.line'  # type: str
    icon_dir = ':open_file_folder:'  # type: str
    icon_file = ':page_facing_up:'  # type: str
    content_box = ROUNDED


def as_tree(layout, real_basedir=False, show_data=False, **kwargs):
    """
    Return :external+rich:py:obj:`~rich.tree.Tree` object representing
    the directory layout. See :ref:`Use cases` for examples.

    Args:
        layout (`~dirlay.Dir`):
            directory layout to be formatted.
        real_basedir (``bool``):
            whether to show real base directory name instead of ``'.'``; defaults to
            ``False``.
        show_data (``bool``):
            whether to include file content in the box under the file name; defaults to
            ``False``.
        kwargs (``Any``):
            optional keyword arguments passed to `~rich.tree.Tree`.

    Returns:
        ``None``
    """
    theme = DefaultTheme

    def label(item, real_path=False):  # type: (Node, bool) -> str
        icon_type = theme.icon_dir if item.is_dir else theme.icon_file
        icon = '' if icon_type is None else '{} '.format(icon_type)
        filename = item.path if real_path else (item.path.name or '.')
        return '{}{}'.format(icon, filename)

    root = layout.root()
    root.path = Path((layout.basedir or '.') if real_basedir else '.')
    tree = Tree(label(root, real_path=real_basedir), **kwargs)
    nodes = {'.': tree}

    for item in sorted(list(layout.values()), key=lambda item: item.key):
        node = (
            Group(label(item), Panel(item.data, theme.content_box, expand=False))
            if show_data and not item.is_dir
            else label(item)
        )
        base = nodes[str(Path(item.key).parent)]
        nodes[item.key] = base.add(node)

    return tree
