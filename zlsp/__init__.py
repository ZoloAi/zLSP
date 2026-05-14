"""
zlsp - Zolo Language Server Protocol

This package provides LSP support for .zolo files.
"""

from .version import __version__

# Main submodules available for import
__all__ = [
    "parser", 
    "cli", 
    "server", 
    "providers", 
    "lsp_types", 
    "token_types",
    "token_registry",
    "exceptions", 
    "version"
]
