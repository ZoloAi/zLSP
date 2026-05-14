"""
LSP providers - Completion, hover, diagnostics, etc.
"""

from .completion import get_completions
from .hover import get_hover_info
from .diagnostics import get_diagnostics

__all__ = ["get_completions", "get_hover_info", "get_diagnostics"]
