try:
    import pathlib
except ImportError:  # pragma: no cover
    import pathlib2 as pathlib  # type: ignore

try:
    import rich
except ImportError:  # pragma: no cover
    rich = None  # type: ignore

__all__ = [
    'pathlib',
    'rich',
]
