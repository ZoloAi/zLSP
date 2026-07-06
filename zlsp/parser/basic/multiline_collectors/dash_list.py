"""
Dash List Collector

Collects YAML-style dash list items (- item1, - item2, etc.) with nested structure support.
Handles multiline items, nested dash lists, and inline objects/arrays within dash items.
"""

import re
from typing import Tuple

# Matches a comma that is NOT already escaped (no preceding backslash).
_UNESCAPED_COMMA = re.compile(r'(?<!\\),')


def _preserve_item_commas(item: str) -> str:
    """
    String-first: a dash item is ONE value, even if it contains commas.

    The reconstructed array (``[a, b, c]``) is re-parsed downstream by
    ``parse_bracket_array`` → ``split_on_comma``, which splits on every top-level
    comma. To keep each ``- ...`` entry whole, escape the content commas of plain
    scalar items so they survive that split. Flow items (inline ``{...}`` objects
    or ``[...]`` arrays) are left untouched — their commas are real separators.
    """
    s = item.lstrip()
    if s.startswith('{') or s.startswith('['):
        return item
    return _UNESCAPED_COMMA.sub(r'\\,', item)


def collect_dash_list(lines: list[str], start_idx: int, parent_indent: int) -> Tuple[str, int, list]:
    """
    Collect YAML-style dash list items (- item1, - item2, etc.) with nested structure support.
    
    Rules:
    - Detect lines starting with "- " at child indent level
    - Collect consecutive dash items
    - Support nested dash lists (standalone dash followed by indented dashes)
    - Stop when indent returns to parent level or less
    - Track each item's line number AND continuation lines for token emission
    
    Args:
        lines: All lines
        start_idx: Index to start collecting from (line after the key)
        parent_indent: Indentation level of the parent key
    
    Returns:
        Tuple of (reconstructed_array_string, lines_consumed, item_line_info)
        - reconstructed_array_string: "[item1, item2, [nested1, nested2]]"
        - lines_consumed: Number of lines consumed
        - item_line_info: List of (line_idx, dash_pos, item_content, continuation_lines) for token emission
          - continuation_lines: List of (line_idx, content) for multiline items
    
    Examples:
        >>> lines = ["  - item1", "  - item2", "  - item3"]
        >>> collect_dash_list(lines, 0, 0)
        ("[item1, item2, item3]", 3, [(0, 2, "item1", []), (1, 2, "item2", []), (2, 2, "item3", [])])
    """
    collected_items = []
    item_line_info = []  # Track (line_idx, dash_position, content, continuation_lines) for each item
    lines_consumed = 0
    expected_indent = None

    i = start_idx
    while i < len(lines):
        line = lines[i]
        line_indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            lines_consumed += 1
            i += 1
            continue

        # Check if line starts with dash (either "- " or just "-" for standalone)
        if stripped.startswith('-') and (stripped == '-' or stripped.startswith('- ')):
            # Set expected indent from first dash item
            if expected_indent is None:
                expected_indent = line_indent

            # Verify this dash is at the expected child indent level
            if line_indent != expected_indent:
                # Different indent level - stop collecting
                break

            # Extract item content (everything after "- " or just the dash)
            if stripped == '-':
                item_content = ''  # Standalone dash
            else:
                item_content = stripped[2:].strip()  # After "- "
            dash_pos = line.index('-')

            if item_content:
                # Check if this is an inline object or array that spans multiple lines
                # Look for unclosed braces or brackets
                open_braces = item_content.count('{') - item_content.count('}')
                open_brackets = item_content.count('[') - item_content.count(']')

                # Check if next line is a natural YAML continuation (indented deeper, not a dash)
                has_natural_continuation = False
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    next_stripped = next_line.strip()
                    # Natural continuation: indented deeper than expected_indent, not a dash, not empty
                    if next_stripped and not next_stripped.startswith('- ') and next_indent > expected_indent:
                        has_natural_continuation = True

                # If we have unclosed braces/brackets OR natural continuations, collect continuation lines
                if open_braces > 0 or open_brackets > 0 or has_natural_continuation:
                    continuation_list = []  # Track (line_idx, content) for each continuation line
                    continuation_parts = []  # For reconstruction
                    continuation_consumed = 0
                    j = i + 1

                    # Continue while we have unclosed braces/brackets OR natural continuations
                    while j < len(lines):
                        cont_line = lines[j]
                        cont_indent = len(cont_line) - len(cont_line.lstrip())
                        cont_stripped = cont_line.strip()

                        # Stop if empty line (natural paragraph break)
                        if not cont_stripped:
                            break

                        # Stop if line is at parent indent or less
                        if cont_indent <= parent_indent:
                            break

                        # Stop if line is at dash indent or less (same level or above this dash)
                        if cont_indent <= expected_indent:
                            break

                        # Stop if line is a dash at same or deeper level (new list item)
                        if cont_stripped.startswith('- '):
                            break

                        # Add this line to continuation
                        continuation_list.append((j, cont_stripped))
                        continuation_parts.append(cont_stripped)

                        # Update bracket/brace counts (for inline objects/arrays)
                        open_braces += cont_stripped.count('{') - cont_stripped.count('}')
                        open_brackets += cont_stripped.count('[') - cont_stripped.count(']')

                        continuation_consumed += 1
                        j += 1

                        # Stop if inline objects/arrays are closed AND next line is not a natural continuation
                        if open_braces == 0 and open_brackets == 0 and j < len(lines):
                            peek_line = lines[j]
                            peek_indent = len(peek_line) - len(peek_line.lstrip())
                            peek_stripped = peek_line.strip()
                            # If next line is not deeper indented, we're done
                            if not peek_stripped or peek_indent <= expected_indent or peek_stripped.startswith('- '):
                                break

                    # Join continuation lines with space for reconstruction
                    if continuation_parts:
                        full_item = item_content + ' ' + ' '.join(continuation_parts)
                    else:
                        full_item = item_content

                    collected_items.append(full_item)
                    item_line_info.append((i, dash_pos, item_content, continuation_list))
                    lines_consumed += 1 + continuation_consumed
                    i += 1 + continuation_consumed
                else:
                    # Regular dash item with content on same line (no multiline)
                    collected_items.append(item_content)
                    item_line_info.append((i, dash_pos, item_content, []))
                    lines_consumed += 1
                    i += 1
            else:
                # Standalone dash - check if there are nested dash items
                item_line_info.append((i, dash_pos, '', []))  # Track standalone dash for tokenization
                lines_consumed += 1

                # Look ahead for nested dash items at deeper indent (next line, i+1)
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    next_stripped = next_line.strip()

                    if next_stripped.startswith('- ') and next_indent > expected_indent:
                        # Recursively collect nested dash list
                        nested_reconstructed, nested_consumed, nested_line_info = collect_dash_list(
                            lines, i + 1, expected_indent
                        )
                        collected_items.append(nested_reconstructed)
                        item_line_info.extend(nested_line_info)
                        lines_consumed += nested_consumed
                        i += nested_consumed + 1  # +1 for the standalone dash we already counted
                    else:
                        # Standalone dash with no nested content - treat as empty string
                        collected_items.append('""')
                        i += 1
                else:
                    # Standalone dash at end of file
                    collected_items.append('""')
                    i += 1
        else:
            # Non-dash line - check if it's at parent indent or less
            if line_indent <= parent_indent:
                # Back to parent level - stop collecting
                break
            else:
                # Deeper indented content that's not a dash list - stop collecting
                break

    # Reconstruct as single-line array format
    if collected_items:
        reconstructed = '[' + ', '.join(_preserve_item_commas(it) for it in collected_items) + ']'
    else:
        reconstructed = '[]'

    return reconstructed, lines_consumed, item_line_info
