"""
Tokenizing Line Parser

Parses lines WITH token emission for LSP semantic highlighting.
Similar to standard parser but emits semantic tokens for all syntax elements.
"""

from typing import TYPE_CHECKING, Optional, Callable

from zlsp.token_types import TokenType
from ...basic.type_hints import TYPE_HINT_PATTERN
from ...zvaf.block_manager import update_all_blocks
from ...zvaf.modifier_handler import ModifierHandler
from ...zvaf.value_validator_callback import validate_for_key_callback
from ..key_value_parser import (
    parse_key_and_emit_root,
    parse_key_and_emit_nested,
    should_enable_multiline_for_key
)
from ...zvaf.key_value_wrapper import (
    parse_key_and_emit_root_zvaf,
    parse_key_and_emit_nested_zvaf,
)
from ..value_emitters import emit_value_tokens
from .multiline_token_handlers import (
    emit_continuation_lines_with_tokens,
    handle_multiline_string_with_tokens,
    handle_bracket_array_with_tokens,
    handle_brace_object_with_tokens,
    handle_dash_list_with_tokens,
)
from .dict_builder import build_nested_dict_zvaf

if TYPE_CHECKING:
    from ..token_emitter import TokenEmitter


def parse_lines_with_tokens(lines: list[str], line_mapping: dict, emitter: 'TokenEmitter') -> dict:
    r"""
    Parse lines with token emission for LSP.
    
    Similar to parse_lines() but emits semantic tokens for all syntax elements.
    """
    if not lines:
        return {}

    structured_lines = []
    i = 0
    line_number = 0

    while i < len(lines):
        line = lines[i]
        original_line_num = line_mapping.get(i, i)
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        if ':' in stripped:
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()

            # Find key position in original line
            key_start = line.find(key)

            # Emit colon token
            colon_pos = line.find(':', key_start)
            emitter.emit(original_line_num, colon_pos, 1, TokenType.COLON)

            # Determine which parser to use (zVaF-aware or basic)
            is_zvaf = ModifierHandler.is_zvaf_file(
                emitter.is_zui_file, emitter.is_zenv_file, emitter.is_zspark_file
            )

            # Check for type hint
            match = TYPE_HINT_PATTERN.match(key)
            if match:
                # Parse and emit key tokens (root or nested)
                if indent == 0:
                    if is_zvaf:
                        clean_key, _, has_str_hint = parse_key_and_emit_root_zvaf(
                            key, line, original_line_num, key_start, indent, emitter
                        )
                    else:
                        clean_key, _, has_str_hint = parse_key_and_emit_root(
                            key, line, original_line_num, key_start, indent, emitter
                        )
                else:
                    # Update block tracking before processing nested keys
                    update_all_blocks(indent, original_line_num, emitter)

                    if is_zvaf:
                        clean_key, _, has_str_hint = parse_key_and_emit_nested_zvaf(
                            key, line, original_line_num, key_start, indent, emitter
                        )
                    else:
                        clean_key, _, has_str_hint = parse_key_and_emit_nested(
                            key, line, original_line_num, key_start, indent, emitter
                        )
            else:
                # No type hint - parse and emit key tokens (root or nested)
                if indent == 0:
                    if is_zvaf:
                        clean_key, _, has_str_hint = parse_key_and_emit_root_zvaf(
                            key, line, original_line_num, key_start, indent, emitter
                        )
                    else:
                        clean_key, _, has_str_hint = parse_key_and_emit_root(
                            key, line, original_line_num, key_start, indent, emitter
                        )
                else:
                    # Update block tracking before processing nested keys
                    update_all_blocks(indent, original_line_num, emitter)

                    if is_zvaf:
                        clean_key, _, has_str_hint = parse_key_and_emit_nested_zvaf(
                            key, line, original_line_num, key_start, indent, emitter
                        )
                    else:
                        clean_key, _, has_str_hint = parse_key_and_emit_nested(
                            key, line, original_line_num, key_start, indent, emitter
                        )

                # No explicit (str) hint - check if this property should auto-enable multiline
                # Use clean_key (without type hint) for auto-multiline detection
                if not has_str_hint:
                    has_str_hint = should_enable_multiline_for_key(clean_key, value, lines, i, indent, emitter)

            # Handle (str) multi-line values OR check for YAML natural continuation
            if has_str_hint:
                structured_line, lines_consumed = handle_multiline_string_with_tokens(
                    lines, i, indent, key, value, line, original_line_num,
                    line_mapping, emitter, colon_pos
                )
                structured_lines.append(structured_line)
                i += lines_consumed + 1
                line_number += lines_consumed + 1
            # Check for YAML natural continuation (even without (str) hint)
            elif value and not value.startswith('[') and not value.startswith('{'):
                # Emit token for the first line value
                value_start = colon_pos + 1
                while value_start < len(line) and line[value_start] == ' ':
                    value_start += 1
                # Pass validator callback if in zvaf mode
                validator = validate_for_key_callback if is_zvaf else None
                emit_value_tokens(value, original_line_num, value_start, emitter, 
                                 value_validator=validator, key=clean_key)

                # Check if next lines are continuation lines (indented more than current).
                # Seed code-fence state if the value already opened a fence.
                in_fence = value.lstrip().startswith('```')
                lines_consumed = emit_continuation_lines_with_tokens(
                    lines, i + 1, indent, line_mapping, emitter,
                    stop_on_key=True,
                    initial_in_code_fence=in_fence
                )

                # Store structured line info (mark as multiline if we found continuations)
                structured_lines.append({
                    'indent': indent,
                    'key': key,
                    'value': value,
                    'line': line,
                    'line_number': original_line_num,
                    'is_multiline': lines_consumed > 0
                })
                i += lines_consumed + 1
                line_number += lines_consumed + 1
            # Handle multi-line arrays (value == '[')
            elif value == '[':
                structured_line, lines_consumed = handle_bracket_array_with_tokens(
                    lines, i, indent, key, value, line, original_line_num,
                    line_mapping, emitter, colon_pos
                )
                structured_lines.append(structured_line)
                i += lines_consumed + 1
                line_number += lines_consumed + 1
            # Handle multi-line objects (value == '{')
            elif value == '{':
                structured_line, lines_consumed = handle_brace_object_with_tokens(
                    lines, i, indent, key, value, line, original_line_num,
                    line_mapping, emitter, colon_pos
                )
                structured_lines.append(structured_line)
                i += lines_consumed + 1
                line_number += lines_consumed + 1
            # Handle dash lists (YAML-style: key:\n  - item1\n  - item2)
            elif not value and i + 1 < len(lines):
                # Check if next line starts with dash at child indent
                next_line = lines[i + 1]
                next_indent = len(next_line) - len(next_line.lstrip())
                next_stripped = next_line.strip()

                if next_stripped.startswith('- ') and next_indent > indent:
                    structured_line, lines_consumed = handle_dash_list_with_tokens(
                        lines, i, indent, key, line, original_line_num,
                        line_mapping, emitter
                    )
                    structured_lines.append(structured_line)
                    i += lines_consumed + 1
                    line_number += lines_consumed + 1
                else:
                    # Empty value (no dash list)
                    structured_lines.append({
                        'indent': indent,
                        'key': key,
                        'value': value,
                        'line': line,
                        'line_number': original_line_num,
                        'is_multiline': False
                    })
                    i += 1
                    line_number += 1
            else:
                # Regular value (not multi-line)
                if value:
                    value_start = colon_pos + 1
                    # Skip whitespace after colon
                    while value_start < len(line) and line[value_start] == ' ':
                        value_start += 1
                    # Extract core key (without modifiers and type hints) for context-aware coloring
                    clean_key = TYPE_HINT_PATTERN.match(key).group(1) if TYPE_HINT_PATTERN.match(key) else key
                    # Only strip modifiers for zVaF files
                    if is_zvaf:
                        _, core_key, _ = ModifierHandler.split_modifiers(clean_key)
                    else:
                        core_key = clean_key
                    validator = validate_for_key_callback if is_zvaf else None
                    emit_value_tokens(value, original_line_num, value_start, emitter, 
                                     key=core_key, value_validator=validator)

                # Store structured line info
                structured_lines.append({
                    'indent': indent,
                    'key': key,
                    'value': value,
                    'line': line,
                    'line_number': original_line_num,
                    'is_multiline': False
                })
                i += 1
                line_number += 1
        else:
            i += 1
            line_number += 1

    # Build nested structure (without token emission, as tokens already emitted)
    # Use zVaF-aware dict builder (supports UI shorthand elements)
    return build_nested_dict_zvaf(structured_lines, 0, 0)
