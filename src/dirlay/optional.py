try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib  # type: ignore

try:
    import rich
except ImportError:
    rich = None  # type: ignore

__all__ = [
    'pathlib',
    'rich',
]
