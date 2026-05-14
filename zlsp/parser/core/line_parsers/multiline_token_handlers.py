"""
Multiline Token Handlers

Consolidated token emission handlers for multiline values:
- Continuation lines
- Multiline strings  
- Bracket arrays
- Dash lists

All handlers used exclusively by tokenizing_parser.py for LSP semantic highlighting.
"""

# Forward reference for type hints
TYPE_CHECKING = False
if TYPE_CHECKING:
    from ..token_emitter import TokenEmitter

import re

from zlsp.token_types import TokenType
from ...basic.multiline_collectors import collect_bracket_array, collect_dash_list
from ...basic.multiline_collectors.brace_object import collect_brace_object
from ...basic.multiline_collectors.str_hint import collect_str_hint_multiline
from ..value_emitters import emit_value_tokens, emit_string_with_escapes

# A line is only a zolo key if the text before the first ':' is a valid
# identifier (letter/underscore/modifier start, alphanumeric body, optional
# type-hint suffix).  This rejects lines like ':vim_cmd', 'https://url',
# '10:30', or '- item:foo' from being treated as keys during continuation.
_KEY_LINE_RE = re.compile(
    r'^[A-Za-z_^~*!][A-Za-z0-9_\-^~*!]*(\([^)]*\))?\s*:'
)


# ============================================================================
# SECTION 1: Continuation Lines
# ============================================================================

def emit_continuation_lines_with_tokens(
    lines: list[str],
    start_idx: int,
    parent_indent: int,
    line_mapping: dict,
    emitter: 'TokenEmitter',
    stop_on_key: bool = True,
    initial_in_code_fence: bool = False
) -> int:
    """
    Collect and emit tokens for continuation lines.
    
    Args:
        lines: All lines
        start_idx: Index to start from
        parent_indent: Parent key indent level
        line_mapping: Maps line index to original line number
        emitter: Token emitter
        stop_on_key: Whether to stop if we encounter a key (has ':')
        initial_in_code_fence: True if a code fence was already opened on the
            parent value line (e.g. ``content: ```vim``), so lines like
            ``:checkhealth lsp`` are not mistaken for zolo keys.
    
    Returns:
        Number of lines consumed
    """
    lines_consumed = 0
    fence_depth = 1 if initial_in_code_fence else 0

    for j in range(start_idx, len(lines)):
        cont_line = lines[j]
        cont_original_line = line_mapping.get(j, j)
        cont_indent = len(cont_line) - len(cont_line.lstrip())
        cont_stripped = cont_line.strip()

        in_code_fence = fence_depth > 0

        # Stop if line is at same or less indent than parent (unless empty or inside fence)
        if cont_stripped and cont_indent <= parent_indent and not in_code_fence:
            break

        # Track fence depth before the stop-on-key check so the closing ```
        # is consumed and fence_depth is correctly updated for lines after it.
        # Use depth counter (not boolean toggle) so nested fences work:
        #   - A line STARTING with ``` closes current fence (depth > 0) or opens new (depth == 0)
        #   - A line CONTAINING ``` inline (e.g. "zCode: ```python") opens an inner fence
        if cont_stripped.startswith('```'):
            if fence_depth > 0:
                fence_depth -= 1  # close current fence
            else:
                fence_depth += 1  # open new fence
        elif '```' in cont_stripped:
            # Inline fence opener (e.g. "zCode: ```python" or "content: ```zui")
            fence_depth += 1

        in_code_fence = fence_depth > 0

        # Stop if this looks like a new key — but not inside a code fence.
        # Use the key-line regex so that bare ':vim_cmd', 'https://url',
        # timestamps, etc. are NOT mistaken for zolo keys.
        if stop_on_key and not in_code_fence and _KEY_LINE_RE.match(cont_stripped):
            break

        # Emit STRING token for this continuation line
        if cont_stripped:
            content_start = len(cont_line) - len(cont_line.lstrip())
            # CODE FENCE FIX: Inside ```zolo blocks, render as plain strings
            # - Inside fences: emit plain STRING (no escape highlighting)
            # - Outside fences: emit with escape sequence highlighting
            # This ensures code examples show uniform cream color in IDE/Bifrost
            if in_code_fence:
                emitter.emit(cont_original_line, content_start, len(cont_stripped), TokenType.STRING)
            else:
                emit_string_with_escapes(cont_stripped, cont_original_line, content_start, emitter)

        lines_consumed += 1

    return lines_consumed


# ============================================================================
# SECTION 2: Multiline Strings
# ============================================================================

def handle_multiline_string_with_tokens(
    lines: list[str],
    i: int,
    indent: int,
    key: str,
    value: str,
    line: str,
    original_line_num: int,
    line_mapping: dict,
    emitter: 'TokenEmitter',
    colon_pos: int
) -> tuple[dict, int]:
    """
    Handle multiline string values with token emission.
    
    Returns:
        Tuple of (structured_line_dict, lines_consumed)
    """
    # Emit value token for first line if present
    if value:
        value_start = colon_pos + 1
        # Skip whitespace after colon
        while value_start < len(line) and line[value_start] == ' ':
            value_start += 1
        # For (str) values, check for escape sequences
        escape_sequences = [
            '\\n', '\\t', '\\r', '\\\\', '\\"', "\\'", '\\u', '\\U'
        ]
        has_valid_escape = any(seq in value for seq in escape_sequences)
        if has_valid_escape:
            emit_string_with_escapes(value, original_line_num, value_start, emitter)
        else:
            emitter.emit(original_line_num, value_start, len(value), TokenType.STRING)

    # Collect and emit tokens for continuation lines.
    # Seed the code-fence state if the opening value already started a fence
    # (e.g. ``content: ```vim``) so that lines like ``:checkhealth lsp`` inside
    # the fence are not mistaken for zolo keys.
    in_fence = bool(value and value.lstrip().startswith('```'))
    lines_consumed = emit_continuation_lines_with_tokens(
        lines, i + 1, indent, line_mapping, emitter,
        stop_on_key=True,
        initial_in_code_fence=in_fence
    )

    # Collect full multiline value for structured_line (matches standard parser)
    # This ensures the 'value' field contains the complete assembled string
    multiline_value, _ = collect_str_hint_multiline(
        lines, i + 1, indent, value, parent_key=key
    )

    # Store structured line info with full multiline value
    structured_line = {
        'indent': indent,
        'key': key,
        'value': multiline_value,
        'line': line,
        'line_number': original_line_num,
        'is_multiline': True
    }
    return structured_line, lines_consumed


# ============================================================================
# SECTION 3: Bracket Arrays
# ============================================================================

def handle_bracket_array_with_tokens(
    lines: list[str],
    i: int,
    indent: int,
    key: str,
    value: str,
    line: str,
    original_line_num: int,
    line_mapping: dict,
    emitter: 'TokenEmitter',
    colon_pos: int
) -> tuple[dict, int]:
    """
    Handle multi-line bracket arrays with token emission.
    
    Returns:
        Tuple of (structured_line_dict, lines_consumed)
    """
    # Find opening bracket position
    value_start = colon_pos + 1
    while value_start < len(line) and line[value_start] == ' ':
        value_start += 1
    bracket_pos = value_start

    # Emit opening bracket
    emitter.emit(original_line_num, bracket_pos, 1, TokenType.BRACKET_STRUCTURAL)

    # Collect multi-line array content
    reconstructed, lines_consumed, item_line_info = collect_bracket_array(
        lines, i + 1, indent, value
    )

    # Emit tokens for each array item line
    for item_line_idx, item_content, has_comma in item_line_info:
        item_original_line = line_mapping.get(item_line_idx, item_line_idx)
        item_line = lines[item_line_idx]
        item_indent = len(item_line) - len(item_line.lstrip())
        stripped_line = item_line.strip()

        # Check if the actual source line is just structural characters
        if stripped_line == '[':
            # Nested array opening - emit bracket token
            bracket_pos = item_line.find('[')
            emitter.emit(item_original_line, bracket_pos, 1, TokenType.BRACKET_STRUCTURAL)
            continue
        elif stripped_line == ']' or stripped_line.startswith(']'):
            # Closing bracket for nested array
            bracket_pos = item_line.find(']')
            emitter.emit(item_original_line, bracket_pos, 1, TokenType.BRACKET_STRUCTURAL)
            continue
        elif stripped_line == '{':
            # Inline object opening - emit brace token
            brace_pos = item_line.find('{')
            emitter.emit(item_original_line, brace_pos, 1, TokenType.BRACE_STRUCTURAL)
            continue
        elif stripped_line == '}' or stripped_line == '},':
            # Inline object closing - emit brace token
            brace_pos = item_line.find('}')
            emitter.emit(item_original_line, brace_pos, 1, TokenType.BRACE_STRUCTURAL)
            # Emit comma if present
            if stripped_line.endswith(','):
                comma_pos = item_line.rfind(',')
                emitter.emit(item_original_line, comma_pos, 1, TokenType.COMMA)
            continue

        # Find where item content starts
        content_start = item_indent

        # Check if this is a key-value pair inside inline object (e.g., "term: value")
        if ':' in stripped_line and not stripped_line.startswith(('- ', '[', ']', '{', '}')):
            colon_pos_inner = stripped_line.find(':')
            if colon_pos_inner > 0:
                item_key = stripped_line[:colon_pos_inner].strip()
                item_value = stripped_line[colon_pos_inner+1:].rstrip(',').strip()

                # Emit key token
                emitter.emit(item_original_line, item_indent, len(item_key), TokenType.NESTED_KEY)

                # Emit colon
                colon_col = item_indent + len(stripped_line[:colon_pos_inner].rstrip())
                emitter.emit(item_original_line, colon_col, 1, TokenType.COLON)

                # Check if value is structural character
                if item_value == '[':
                    # Emit bracket structural token
                    bracket_pos = item_line.find('[', colon_col + 1)
                    if bracket_pos >= 0:
                        emitter.emit(item_original_line, bracket_pos, 1, TokenType.BRACKET_STRUCTURAL)
                elif item_value == '{':
                    # Emit brace structural token
                    brace_pos = item_line.find('{', colon_col + 1)
                    if brace_pos >= 0:
                        emitter.emit(item_original_line, brace_pos, 1, TokenType.BRACE_STRUCTURAL)
                else:
                    # Emit value tokens for regular content
                    value_start_inner = stripped_line.find(item_value, colon_pos_inner)
                    if value_start_inner >= 0:
                        value_col = item_indent + value_start_inner
                        emit_value_tokens(item_value, item_original_line, value_col, emitter)

                # Emit comma if present
                if has_comma:
                    comma_pos = item_line.rfind(',')
                    if comma_pos >= 0:
                        emitter.emit(item_original_line, comma_pos, 1, TokenType.COMMA)
                continue

        # Regular item - emit token for the item content
        emit_value_tokens(item_content, item_original_line, content_start, emitter)

        # Emit comma if present
        if has_comma:
            comma_pos = item_indent + len(item_content)
            emitter.emit(item_original_line, comma_pos, 1, TokenType.COMMA)

    # Find and emit closing bracket
    closing_line_idx = i + lines_consumed
    if closing_line_idx < len(lines):
        closing_line = lines[closing_line_idx]
        closing_original_line = line_mapping.get(closing_line_idx, closing_line_idx)
        closing_bracket_pos = closing_line.find(']')
        if closing_bracket_pos >= 0:
            emitter.emit(closing_original_line, closing_bracket_pos, 1, TokenType.BRACKET_STRUCTURAL)

    # Store structured line info with reconstructed value
    structured_line = {
        'indent': indent,
        'key': key,
        'value': reconstructed,
        'line': line,
        'line_number': original_line_num,
        'is_multiline': True,
        'multiline_type': 'array'  # Mark as array for type detection
    }
    return structured_line, lines_consumed


def handle_brace_object_with_tokens(
    lines: list[str],
    i: int,
    indent: int,
    key: str,
    value: str,
    line: str,
    original_line_num: int,
    line_mapping: dict,
    emitter: 'TokenEmitter',
    colon_pos: int
) -> tuple[dict, int]:
    """
    Handle multi-line brace objects with token emission.
    
    Returns:
        Tuple of (structured_line_dict, lines_consumed)
    """
    # Find opening brace position
    value_start = colon_pos + 1
    while value_start < len(line) and line[value_start] == ' ':
        value_start += 1
    brace_pos = value_start

    # Emit opening brace
    emitter.emit(original_line_num, brace_pos, 1, TokenType.BRACE_STRUCTURAL)

    # Collect multi-line object content
    reconstructed, lines_consumed, pair_line_info = collect_brace_object(
        lines, i + 1, indent, value
    )

    # Emit tokens for each object pair line
    for pair_line_idx, pair_content, has_comma in pair_line_info:
        pair_original_line = line_mapping.get(pair_line_idx, pair_line_idx)
        pair_line = lines[pair_line_idx]
        pair_indent = len(pair_line) - len(pair_line.lstrip())
        stripped_line = pair_line.strip()

        # Check if the actual source line is just structural characters
        if stripped_line == '{':
            # Nested object opening - emit brace token
            brace_pos_inner = pair_line.find('{')
            emitter.emit(pair_original_line, brace_pos_inner, 1, TokenType.BRACE_STRUCTURAL)
            continue
        elif stripped_line == '}' or stripped_line.startswith('}'):
            # Closing brace for nested object
            brace_pos_inner = pair_line.find('}')
            emitter.emit(pair_original_line, brace_pos_inner, 1, TokenType.BRACE_STRUCTURAL)
            continue
        elif stripped_line == '[':
            # Inline array opening - emit bracket token
            bracket_pos = pair_line.find('[')
            emitter.emit(pair_original_line, bracket_pos, 1, TokenType.BRACKET_STRUCTURAL)
            continue
        elif stripped_line == ']' or stripped_line == '],':
            # Inline array closing - emit bracket token
            bracket_pos = pair_line.find(']')
            emitter.emit(pair_original_line, bracket_pos, 1, TokenType.BRACKET_STRUCTURAL)
            # Emit comma if present
            if stripped_line.endswith(','):
                comma_pos = pair_line.rfind(',')
                emitter.emit(pair_original_line, comma_pos, 1, TokenType.COMMA)
            continue

        # Check if this is a key-value pair (e.g., "id: 42")
        if ':' in stripped_line and not stripped_line.startswith(('{', '}', '[', ']')):
            colon_pos_inner = stripped_line.find(':')
            if colon_pos_inner > 0:
                pair_key = stripped_line[:colon_pos_inner].strip()
                pair_value = stripped_line[colon_pos_inner+1:].rstrip(',').strip()

                # Check for type hint in key
                from zlsp.parser.basic.type_hints import TYPE_HINT_PATTERN
                type_hint_match = TYPE_HINT_PATTERN.match(pair_key)
                if type_hint_match:
                    clean_key = type_hint_match.group(1)
                    type_hint = type_hint_match.group(2)
                    
                    # Emit key token
                    emitter.emit(pair_original_line, pair_indent, len(clean_key), TokenType.NESTED_KEY)
                    
                    # Emit type hint tokens
                    hint_start = pair_indent + len(clean_key)
                    emitter.emit(pair_original_line, hint_start, 1, TokenType.TYPE_HINT_PAREN)  # (
                    emitter.emit(pair_original_line, hint_start + 1, len(type_hint), TokenType.TYPE_HINT)
                    emitter.emit(pair_original_line, hint_start + 1 + len(type_hint), 1, TokenType.TYPE_HINT_PAREN)  # )
                else:
                    clean_key = pair_key
                    type_hint = None
                    # Emit key token
                    emitter.emit(pair_original_line, pair_indent, len(pair_key), TokenType.NESTED_KEY)

                # Emit colon
                colon_col = pair_indent + len(stripped_line[:colon_pos_inner].rstrip())
                emitter.emit(pair_original_line, colon_col, 1, TokenType.COLON)

                # Check if value is structural character
                if pair_value == '[':
                    # Emit bracket structural token
                    bracket_pos = pair_line.find('[', colon_col + 1)
                    if bracket_pos >= 0:
                        emitter.emit(pair_original_line, bracket_pos, 1, TokenType.BRACKET_STRUCTURAL)
                elif pair_value == '{':
                    # Emit brace structural token
                    brace_pos_inner = pair_line.find('{', colon_col + 1)
                    if brace_pos_inner >= 0:
                        emitter.emit(pair_original_line, brace_pos_inner, 1, TokenType.BRACE_STRUCTURAL)
                else:
                    # Emit value tokens for regular content
                    value_start_inner = stripped_line.find(pair_value, colon_pos_inner)
                    if value_start_inner >= 0:
                        value_col = pair_indent + value_start_inner
                        # Pass type hint if present
                        emit_value_tokens(pair_value, pair_original_line, value_col, emitter, type_hint=type_hint)

                # Emit comma if present
                if has_comma:
                    comma_pos = pair_line.rfind(',')
                    if comma_pos >= 0:
                        emitter.emit(pair_original_line, comma_pos, 1, TokenType.COMMA)
                continue

    # The collector adds closing braces for NESTED objects to pair_line_info,
    # but NOT the closing brace for THIS level (it breaks before adding it).
    # So we need to emit the closing brace for THIS level here.
    # Check if the last item in pair_line_info is a closing brace - if not, emit it.
    needs_closing_brace = True
    if pair_line_info and pair_line_info[-1][1] == '}':
        # Last item is already a closing brace, check if it's at the right level
        # by comparing line indices
        last_brace_idx = pair_line_info[-1][0]
        expected_closing_idx = i + lines_consumed
        if last_brace_idx == expected_closing_idx:
            needs_closing_brace = False

    if needs_closing_brace:
        closing_line_idx = i + lines_consumed
        if closing_line_idx < len(lines):
            closing_line = lines[closing_line_idx]
            closing_original_line = line_mapping.get(closing_line_idx, closing_line_idx)
            closing_brace_pos = closing_line.find('}')
            if closing_brace_pos >= 0:
                emitter.emit(closing_original_line, closing_brace_pos, 1, TokenType.BRACE_STRUCTURAL)

    # Store structured line info with reconstructed value
    structured_line = {
        'indent': indent,
        'key': key,
        'value': reconstructed,
        'line': line,
        'line_number': original_line_num,
        'is_multiline': True,
        'multiline_type': 'object'  # Mark as object for type detection
    }
    return structured_line, lines_consumed


# ============================================================================
# SECTION 4: Dash Lists
# ============================================================================

def handle_dash_list_with_tokens(
    lines: list[str],
    i: int,
    indent: int,
    key: str,
    line: str,
    original_line_num: int,
    line_mapping: dict,
    emitter: 'TokenEmitter'
) -> tuple[dict, int]:
    """
    Handle dash list values with token emission.
    
    Returns:
        Tuple of (structured_line_dict, lines_consumed)
    """
    # Collect dash list items
    reconstructed, lines_consumed, item_line_info = collect_dash_list(lines, i + 1, indent)

    # Emit tokens for each dash list item line
    for item_info in item_line_info:
        # Unpack item info (may or may not have continuation_lines)
        if len(item_info) == 4:
            item_line_idx, dash_pos, item_content, continuation_lines = item_info
        else:
            # Legacy format without continuation_lines
            item_line_idx, dash_pos, item_content = item_info
            continuation_lines = []

        item_original_line = line_mapping.get(item_line_idx, item_line_idx)

        # Emit dash as BRACKET_STRUCTURAL (same color as [ ])
        emitter.emit(item_original_line, dash_pos, 1, TokenType.BRACKET_STRUCTURAL)

        # Emit token for the item content (after "- ")
        content_start = dash_pos + 2  # After "- "
        emit_value_tokens(item_content, item_original_line, content_start, emitter)

        # Parse and tokenize continuation lines (multiline content within inline objects/arrays)
        for cont_line_idx, _ in continuation_lines:
            cont_original_line = line_mapping.get(cont_line_idx, cont_line_idx)
            cont_line_text = lines[cont_line_idx]
            cont_indent = len(cont_line_text) - len(cont_line_text.lstrip())
            cont_stripped = cont_line_text.strip()

            if cont_stripped:
                # Check if this line contains a key-value pair (has ':' not in quotes)
                if ':' in cont_stripped and not cont_stripped.startswith(('- ', '[', ']', '{', '}')):
                    # Parse as key-value pair (e.g., "term: value,")
                    colon_pos_inner = cont_stripped.find(':')
                    if colon_pos_inner > 0:
                        cont_key = cont_stripped[:colon_pos_inner].strip()
                        cont_value = cont_stripped[colon_pos_inner+1:].strip()

                        # Emit key token
                        emitter.emit(
                            cont_original_line, cont_indent,
                            len(cont_key), TokenType.NESTED_KEY
                        )

                        # Emit colon
                        colon_col = cont_indent + len(cont_stripped[:colon_pos_inner].rstrip())
                        emitter.emit(cont_original_line, colon_col, 1, TokenType.COLON)

                        # Emit value tokens (handles comma, brackets, etc.)
                        stripped_after_colon = cont_stripped[colon_pos_inner+1:]
                        value_col = (cont_indent + colon_pos_inner + 1 +
                                     (len(stripped_after_colon) - len(cont_value)))
                        emit_value_tokens(
                            cont_value, cont_original_line, value_col, emitter
                        )
                        continue

                # Otherwise, parse as structured value (brackets, braces, strings, etc.)
                emit_value_tokens(cont_stripped, cont_original_line, cont_indent, emitter)

    # Store structured line info with reconstructed value
    structured_line = {
        'indent': indent,
        'key': key,
        'value': reconstructed,
        'line': line,
        'line_number': original_line_num,
        'is_multiline': True,
        'multiline_type': 'dash_list'  # Mark as dash list for type detection
    }
    return structured_line, lines_consumed
