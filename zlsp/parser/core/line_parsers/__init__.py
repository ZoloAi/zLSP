"""
Line Parsers - Modular parsing logic

Provides core line parsing functionality split into focused modules.
Each module handles a specific aspect of parsing for better maintainability.

Separation:
- parse_lines: Basic JSON/YAML parser (extensible via callbacks)
- build_nested_dict: Basic dict builder (strict duplicate checking)
- build_nested_dict_zvaf: zVaF dict builder (UI shorthand support)

Note: parse_lines_zvaf moved to zvaf/ folder for better separation
"""

from .indentation import check_indentation_consistency
from .tokenizing_parser import parse_lines_with_tokens
from .standard_parser import parse_lines
from .dict_builder import build_nested_dict, build_nested_dict_zvaf
from .root_parser import parse_root_key_value_pairs

__all__ = [
    'check_indentation_consistency',
    'parse_lines_with_tokens',
    'parse_lines',
    'build_nested_dict',
    'build_nested_dict_zvaf',
    'parse_root_key_value_pairs',
]
