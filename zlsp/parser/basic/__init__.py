"""
Basic Parser Components - Format-agnostic parsing primitives

These modules contain pure parsing components without knowledge of
zVaF-specific file types or semantics. Reusable for any structured format.
"""

from .block_tracker import BlockTracker
from .type_hints import process_type_hints, TYPE_HINT_PATTERN
from .serializer import dumps as serialize_zolo
from .validators import (
    validate_ascii_only,
    is_zpath_value,
    is_env_config_value,
    is_valid_number,
)
from .escape_processors import (
    decode_unicode_escapes,
    process_escape_sequences,
)
from .value_processors import (
    detect_value_type,
    parse_brace_object,
    parse_bracket_array,
    split_on_comma,
)
from .multiline_collectors import (
    collect_str_hint_multiline,
    collect_dash_list,
    collect_bracket_array,
    collect_pipe_multiline,
    collect_triple_quote_multiline,
)
from .comment_processors import (
    strip_comments_and_prepare_lines,
    strip_comments_and_prepare_lines_with_tokens,
)
from .error_formatter import ErrorFormatter, did_you_mean

__all__ = [
    'BlockTracker',
    'process_type_hints',
    'TYPE_HINT_PATTERN',
    'serialize_zolo',
    'validate_ascii_only',
    'is_zpath_value',
    'is_env_config_value',
    'is_valid_number',
    'decode_unicode_escapes',
    'process_escape_sequences',
    'detect_value_type',
    'parse_brace_object',
    'parse_bracket_array',
    'split_on_comma',
    'collect_str_hint_multiline',
    'collect_dash_list',
    'collect_bracket_array',
    'collect_pipe_multiline',
    'collect_triple_quote_multiline',
    'strip_comments_and_prepare_lines',
    'strip_comments_and_prepare_lines_with_tokens',
    'ErrorFormatter',
    'did_you_mean',
]
