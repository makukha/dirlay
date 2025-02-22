try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Optional  # noqa: F401  # used in type hint comment

from rich.box import ROUNDED
from rich.panel import Panel
from rich.tree import Tree

try:
    from rich.console import Group
except ImportError:
    from rich.group import Group


class DefaultTheme:
    style = 'tree'  # type: str
    guide_style = 'tree.line'  # type: str
    icon_dir = ':open_file_folder:'  # type: str
    icon_file = ':page_facing_up:'  # type: str
    content_box = ROUNDED


def to_tree(layout, real_basedir=False, show_content=False, **kwargs):
    """
    Return :external+rich:py:obj:`~rich.tree.Tree` object representing
    the directory layout. See :ref:`Use cases` for examples.

    Args:
        layout (`~dirlay.DirLayout`):
            directory layout to be formatted.
        real_basedir (``bool``):
            whether to show real base directory name instead of ``'.'``; defaults to
            ``False``.
        show_content (``bool``):
            whether to include file content in the box under the file name; defaults to
            ``False``.
        kwargs (``Any``):
            optional keyword arguments passed to `~rich.tree.Tree`.

    Returns:
        ``None``
    """
    if Tree is NotImplemented:
        raise NotImplementedError(
            'Optional dependency rich is required; install as dirlay[rich]'
        )

    theme = DefaultTheme

    def nodename(path, value):  # type: (str, Optional[str]) -> str
        icon_type = theme.icon_dir if value is None else theme.icon_file
        icon = '' if icon_type is None else '{} '.format(icon_type)
        return '{}{}'.format(icon, path)

    basedir = str(layout.basedir) or '.'
    tree = Tree(nodename(basedir if real_basedir else '.', None), **kwargs)
    nodes = {'.': tree}

    for path, value in layout:
        filename = nodename(path.name, value)
        if show_content and value is not None:
            node = Group(filename, Panel(value, box=theme.content_box, expand=False))
        else:
            node = filename
        base = nodes[str(path.parent)]
        nodes[str(path)] = base.add(node)

    return tree
