"""
Compatibility shim: some code may import `middlewear` (misspelling).
This module re-exports middleware.* so both imports work.
"""

from .middleware import *  # noqa: F401,F403