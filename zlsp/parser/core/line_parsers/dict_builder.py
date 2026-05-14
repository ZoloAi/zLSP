"""
Dictionary Builder

Recursively builds nested dictionaries from structured lines.
Handles type detection and duplicate key checking.

Separation:
- Core logic: Generic JSON/YAML-like dict building (basic)
- zVaF extensions: UI shorthand handling via duplicate_key_handler

Usage:
- build_nested_dict(): Basic JSON/YAML mode (strict duplicate checking)
- build_nested_dict_zvaf(): zVaF mode (UI shorthand support)
"""

from typing import Callable, Optional

from zlsp.exceptions import ZoloParseError
from ...basic.type_hints import TYPE_HINT_PATTERN
from ...basic.value_processors import detect_value_type
from ...basic.escape_processors import decode_unicode_escapes
from ...basic.error_formatter import ErrorFormatter


def build_nested_dict(
    structured_lines: list[dict],
    start_idx: int,
    current_indent: int,
    duplicate_key_handler: Optional[Callable[[str, str, dict, int, str], tuple[bool, str]]] = None
) -> dict:
    """
    Recursively build nested dictionary from structured lines.
    
    BASIC FEATURE: Generic JSON/YAML-like dict building with strict duplicate checking.
    EXTENSION POINT: Pass duplicate_key_handler for domain-specific behavior (e.g., zVaF UI shorthands).
    
    Args:
        structured_lines: List of parsed line dictionaries
        start_idx: Index to start parsing from
        current_indent: Current indentation level we're parsing at
        duplicate_key_handler: Optional callback for custom duplicate key handling.
                              Signature: (clean_key, original_key, result_dict,
                              line_number, first_key) -> (should_exempt, final_key)
                              - should_exempt: True to skip duplicate error
                              - final_key: Key to use in result dict (may be suffixed)
    
    Returns:
        Nested dictionary
    
    Raises:
        ZoloParseError: If duplicate keys are found at the same nesting level (unless exempted by handler)
    """
    result = {}
    seen_keys = {}  # Track: {clean_key: (line_number, original_key)}
    i = start_idx

    while i < len(structured_lines):
        line_info = structured_lines[i]
        indent = line_info['indent']
        key = line_info['key']
        value = line_info['value']
        line_number = line_info.get('line_number', '?')

        # If we've moved to a different indent level, stop
        if indent != current_indent:
            break

        # Strip type hint from key for duplicate checking (BASIC FEATURE)
        # Example: "port(int)" → "port"
        match = TYPE_HINT_PATTERN.match(key)
        clean_key = match.group(1) if match else key

        # Check for duplicate keys (BASIC FEATURE - STRICT MODE)
        should_exempt_from_dup_check = False
        if clean_key in seen_keys:
            first_line, first_key = seen_keys[clean_key]

            # Extension point: Allow custom handler to override duplicate behavior
            if duplicate_key_handler:
                should_exempt_from_dup_check, _ = duplicate_key_handler(
                    clean_key, key, result, line_number, first_key
                )

            # Raise error if not exempted (BASIC STRICT BEHAVIOR)
            if not should_exempt_from_dup_check:
                error_msg = ErrorFormatter.format_duplicate_key_error(
                    duplicate_key=clean_key,
                    first_line=first_line,
                    current_line=line_number,
                    first_key_raw=first_key
                )
                raise ZoloParseError(error_msg)

        # Track seen keys for duplicate detection
        seen_keys[clean_key] = (line_number, key)

        # Check if next line is a child (more indented) - BASIC FEATURE
        has_children = False
        child_indent = None
        if i + 1 < len(structured_lines):
            next_indent = structured_lines[i + 1]['indent']
            if next_indent > indent:
                has_children = True
                child_indent = next_indent

        if has_children:
            # Recursively parse children (BASIC FEATURE)
            child_dict = build_nested_dict(
                structured_lines, i + 1, child_indent, duplicate_key_handler
            )

            # Determine final key (extension point for domain-specific handling)
            final_key = key
            if duplicate_key_handler and key in result:
                # Handler may suffix key for duplicate preservation
                _, final_key = duplicate_key_handler(
                    clean_key, key, result, line_number, key
                )

            result[final_key] = child_dict

            # Skip all child lines (find next line at current indent or less)
            i += 1
            while i < len(structured_lines) and structured_lines[i]['indent'] > indent:
                i += 1
        else:
            # Leaf node - detect value type or use multi-line string (BASIC FEATURE)
            if line_info.get('is_multiline', False):
                # Check if it's a multi-line array/dash list (needs type detection) or string (use as-is)
                if line_info.get('multiline_type') in ('array', 'dash_list'):
                    # Multi-line array or dash list: run type detection on reconstructed value
                    typed_value = detect_value_type(value) if value else ''
                else:
                    # Multi-line string: decode escape sequences (\n, \t, etc.) but skip type detection
                    # This ensures \n in markdown content becomes actual newlines
                    # EXCEPTION: Code fence content (```...) should NOT have escapes decoded
                    # because \n in code should remain literal \n for Python/JS/etc.
                    if value and value.lstrip().startswith('```'):
                        typed_value = value  # Preserve code fence content as-is
                    else:
                        typed_value = decode_unicode_escapes(value) if value else ''
            else:
                # Detect value type (including \n escape sequences)
                typed_value = detect_value_type(value) if value else ''

            # Determine final key (extension point for domain-specific handling)
            final_key = key
            if duplicate_key_handler and key in result:
                # Handler may suffix key for duplicate preservation
                _, final_key = duplicate_key_handler(
                    clean_key, key, result, line_number, key
                )

            result[final_key] = typed_value
            i += 1

    return result


# ============================================================================
# zVaF-Specific Extension
# ============================================================================

def _zvaf_duplicate_key_handler(
    clean_key: str,
    original_key: str,
    result_dict: dict,
    _line_number: int,
    _first_key: str
) -> tuple[bool, str]:
    """
    zVaF-specific duplicate key handler for UI event shorthands.
    
    UI elements (zText, zButton, etc.) can appear multiple times in sequence,
    so they're exempt from duplicate checks and get suffixed keys.
    
    Returns:
        (should_exempt_from_error, final_key_to_use)
    """
    from ...zvaf import is_ui_event_shorthand, handle_duplicate_ui_key
    
    is_ui_shorthand = is_ui_event_shorthand(clean_key)
    
    if is_ui_shorthand:
        # Exempt from duplicate error and generate suffixed key
        final_key = handle_duplicate_ui_key(original_key, result_dict)
        return (True, final_key)
    else:
        # Not a UI shorthand - use standard duplicate error
        return (False, original_key)


def build_nested_dict_zvaf(
    structured_lines: list[dict],
    start_idx: int = 0,
    current_indent: int = 0
) -> dict:
    """
    Build nested dict with zVaF-specific UI shorthand support.
    
    This is a convenience wrapper around build_nested_dict() that enables:
    - UI event shorthand exemptions (zText, zButton, etc. can repeat)
    - Automatic key suffixing for duplicate UI elements
    
    Args:
        structured_lines: List of parsed line dictionaries
        start_idx: Index to start parsing from (default: 0)
        current_indent: Current indentation level (default: 0)
    
    Returns:
        Nested dictionary with zVaF UI shorthand handling
    """
    return build_nested_dict(
        structured_lines,
        start_idx,
        current_indent,
        duplicate_key_handler=_zvaf_duplicate_key_handler
    )
