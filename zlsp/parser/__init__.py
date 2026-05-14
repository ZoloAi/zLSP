"""
Zolo parser - Single source of truth for .zolo file parsing.

Main entry points (with automatic file-type routing):
- tokenize() - Parse with semantic tokens (LSP)
- loads() - Parse without tokens (runtime)
- load() - Load from file
- dumps() - Serialize to string
- dump() - Write to file

Architecture:
- parser_service.py: Entry point with file type detection and routing
- parser.py: Internal implementation (tokenize_basic/zvaf, loads_basic/zvaf)
- basic/: Core parsing features (type hints, indentation, etc.)
- zvaf/: zVaF extensions (modifiers, UI shorthands, etc.)
"""

from .parser import load, dump, dumps
from .parser_service import tokenize, loads
from .basic import process_type_hints

__all__ = [
    # Main API (with automatic routing)
    "tokenize",  # Parse with tokens (LSP)
    "loads",     # Parse without tokens (runtime)
    "load",      # Load from file
    "dumps",     # Serialize to string
    "dump",      # Write to file
    
    # Utilities
    "process_type_hints",
]
