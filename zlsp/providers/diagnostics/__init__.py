"""Diagnostics provider for .zolo files."""

from .diagnostic_provider import get_diagnostics, get_all_diagnostics
from .formatter import DiagnosticFormatter

__all__ = [
    'get_diagnostics',
    'get_all_diagnostics',
    'DiagnosticFormatter',
]
