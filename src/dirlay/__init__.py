try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # type: ignore[import-not-found,no-redef]

from dirlay.dir import DirLayout


__version__ = '0.0.0'

__all__ = [
    '__version__',
    'DirLayout',
    'Path',
]
