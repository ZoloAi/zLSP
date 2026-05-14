"""
Core Integration Layer - Orchestration and coordination

These modules coordinate basic and zVaF-specific components to provide
the complete parsing functionality with token emission and state management.
"""

from .token_emitter import TokenEmitter
from .value_emitters import (
    emit_value_tokens,
    emit_string_with_escapes,
    emit_array_tokens,
    emit_object_tokens,
)
from .line_parsers import (
    parse_lines_with_tokens,
    parse_lines,
    build_nested_dict,
    build_nested_dict_zvaf,
    parse_root_key_value_pairs,
    check_indentation_consistency,
)

__all__ = [
    'TokenEmitter',
    'emit_value_tokens',
    'emit_string_with_escapes',
    'emit_array_tokens',
    'emit_object_tokens',
    'parse_lines_with_tokens',
    'parse_lines',
    'build_nested_dict',
    'build_nested_dict_zvaf',
    'parse_root_key_value_pairs',
    'check_indentation_consistency',
]
