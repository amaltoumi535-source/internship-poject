"""Top-level package for app modules.

Keeps the package importable and provides small helpers to inspect or import
submodules under app.modules dynamically.

Example:
    from app.modules import list_modules, import_module_by_name
    print(list_modules())                   # ['storage', 'ingestion', ...]
    storage = import_module_by_name('storage')
"""
from importlib import import_module
from pkgutil import iter_modules
from typing import List

__all__ = ["list_modules", "import_module_by_name"]


def list_modules() -> List[str]:
    """
    Return the names of immediate submodules/packages under app.modules.
    Useful for runtime discovery when including optional routers.
    """
    return [name for _, name, _ in iter_modules(__path__)]


def import_module_by_name(name: str):
    """
    Import and return a submodule under app.modules by its short name.

    Example: import_module_by_name('storage') -> app.modules.storage
    Raises ImportError if the module cannot be imported.
    """
    return import_module(f"{__name__}.{name}")