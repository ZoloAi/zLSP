"""
Standard Line Parser

Parses lines without token emission (for runtime use).
Builds nested dictionary structure with multiline support.

Separation:
- BASIC: JSON/YAML-like parsing (indentation, type hints, arrays, dash lists)
- EXTENSION: Optional callbacks for domain-specific behavior (e.g., zVaF)
"""

from typing import Callable, Optional
from ...basic.type_hints import TYPE_HINT_PATTERN
from ...basic.multiline_collectors import (
    collect_str_hint_multiline,
    collect_dash_list,
    collect_bracket_array,
)
from ...basic.validators import validate_ascii_only
from .dict_builder import build_nested_dict


def parse_lines(
    lines: list[str],
    line_mapping: dict = None,
    auto_multiline_checker: Optional[Callable] = None,
    dict_builder: Optional[Callable] = None
) -> dict:
    r"""
    Phase 2, Step 2.3 + Phase 3: Parse lines with nested object and multi-line string support.
    
    BASIC MODE (default): JSON/YAML-like parsing
    - Indentation-based nesting
    - Type hints: key(type)
    - Multiline: (str) hint required
    - Arrays: bracket notation [...]
    - Dash lists: YAML-style
    
    EXTENSION MODE (via callbacks):
    - auto_multiline_checker: Custom logic for auto-enabling multiline (e.g., zVaF UI props)
    - dict_builder: Custom dict builder (e.g., zVaF UI shorthand support)
    
    Args:
        lines: Cleaned lines (from Step 1.1)
        line_mapping: Optional dict mapping cleaned line index to original line number (1-based)
        auto_multiline_checker: Optional callback(key, value, indent, structured_lines, lines, i)
                               Returns (enable_multiline: bool, parent_key: str|None)
        dict_builder: Optional dict builder function (default: build_nested_dict)
    
    Returns:
        Nested dictionary structure
    
    Examples:
        >>> parse_lines(["name: MyApp", "port: 5000"])
        {'name': 'MyApp', 'port': 5000.0}
        
        >>> parse_lines(["server:", "  host: localhost", "  port: 5000"])
        {'server': {'host': 'localhost', 'port': 5000.0}}
    """
    if not lines:
        return {}

    # Default line mapping if not provided (for backwards compatibility)
    if line_mapping is None:
        line_mapping = {i: i + 1 for i in range(len(lines))}

    # Default to basic dict builder if not provided
    if dict_builder is None:
        dict_builder = build_nested_dict

    # Parse lines into structured data with indentation info and multi-line handling
    structured_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Get original line number from mapping
        original_line_number = line_mapping.get(i, i + 1)

        if ':' in stripped:
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()

            # Validate key is ASCII-only (RFC 8259 compliance)
            # NEW: Set strict=False to allow emojis in keys (LSP provides INFO hints)
            validate_ascii_only(key, original_line_number, strict=False)

            # Check if key has (str) type hint for multi-line collection
            match = TYPE_HINT_PATTERN.match(key)
            has_str_hint = match and match.group(2).lower() == 'str'

            # EXTENSION: Check if this property should auto-enable multiline (domain-specific)
            parent_block_key = None  # Track parent block for semantic joining
            if not has_str_hint and auto_multiline_checker:
                has_str_hint, parent_block_key = auto_multiline_checker(
                    key, value, indent, structured_lines, lines, i
                )

            # Multi-line enabled with (str) hint OR auto-multiline property
            if has_str_hint:
                # For zMD content, preserve trailing whitespace (double-space line breaks)
                # Re-extract value without stripping trailing space
                if parent_block_key and parent_block_key.lower() == 'zmd':
                    # Get original line to preserve trailing spaces
                    original_value = line[line.index(':') + 1:].lstrip()
                else:
                    original_value = value
                
                # (str) type hint: collect YAML-style indented multi-line
                # Pass the parent block key for semantic joining (zText vs zMD)
                multiline_value, lines_consumed = collect_str_hint_multiline(
                    lines, i + 1, indent, original_value,
                    parent_key=parent_block_key or key
                )
                structured_lines.append({
                    'indent': indent,
                    'key': key,
                    'value': multiline_value,
                    'line': line,
                    'line_number': original_line_number,
                    'is_multiline': True
                })
                i += lines_consumed + 1
            # Handle multi-line arrays (value == '[')
            elif value == '[':
                # Collect multi-line array content
                reconstructed, lines_consumed, _ = collect_bracket_array(lines, i + 1, indent, value)
                structured_lines.append({
                    'indent': indent,
                    'key': key,
                    'value': reconstructed,
                    'line': line,
                    'line_number': original_line_number,
                    'is_multiline': True,
                    'multiline_type': 'array'  # Mark as array for type detection
                })
                i += lines_consumed + 1
            # Handle dash lists (YAML-style: key:\n  - item1\n  - item2)
            elif not value and i + 1 < len(lines):
                # Check if next line starts with dash at child indent
                next_line = lines[i + 1]
                next_indent = len(next_line) - len(next_line.lstrip())
                next_stripped = next_line.strip()

                if next_stripped.startswith('- ') and next_indent > indent:
                    # Collect dash list items
                    reconstructed, lines_consumed, _ = collect_dash_list(lines, i + 1, indent)
                    structured_lines.append({
                        'indent': indent,
                        'key': key,
                        'value': reconstructed,
                        'line': line,
                        'line_number': original_line_number,
                        'is_multiline': True,
                        'multiline_type': 'dash_list'  # Mark as dash list for type detection
                    })
                    i += lines_consumed + 1
                else:
                    # Empty value (no dash list)
                    structured_lines.append({
                        'indent': indent,
                        'key': key,
                        'value': value,
                        'line': line,
                        'line_number': original_line_number,
                        'is_multiline': False
                    })
                    i += 1
            else:
                # Regular value - | and """ are literal characters
                structured_lines.append({
                    'indent': indent,
                    'key': key,
                    'value': value,
                    'line': line,
                    'line_number': original_line_number,
                    'is_multiline': False
                })
                i += 1
        else:
            i += 1

    # Build nested structure using provided or default dict builder
    return dict_builder(structured_lines, 0, 0)
