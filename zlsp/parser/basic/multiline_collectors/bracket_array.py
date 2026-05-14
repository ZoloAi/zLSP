"""
Bracket Array Collector

Collects multi-line array content from opening [ to closing ].
Supports nested arrays and inline objects within arrays.
"""

from typing import Tuple


def collect_bracket_array(
    lines: list[str], start_idx: int, parent_indent: int, _first_value: str
) -> Tuple[str, int, list]:
    """
    Collect multi-line array content from opening [ to closing ].
    
    SUPPORTS NESTED ARRAYS:
    - Recursively handles nested [nested_items] within arrays
    - Properly tracks bracket depth to find matching closing ]
    
    Rules:
    - Opening [ is on the key line (first_value = '[')
    - Collect lines indented MORE than parent
    - Stop when we find ] that closes THIS array level
    - Track each item's line number for token emission
    
    Args:
        lines: All lines
        start_idx: Index to start collecting from (line after opening [)
        parent_indent: Indentation level of the parent key with opening [
        _first_value: The value on the same line as the key (should be '[')
    
    Returns:
        Tuple of (reconstructed_array_string, lines_consumed, item_line_info)
        - reconstructed_array_string: "[item1, item2, [nested1, nested2]]"
        - lines_consumed: Number of lines consumed (NOT including opening [)
        - item_line_info: List of (line_idx, item_content, has_comma) for token emission
    
    Examples:
        >>> lines = ["  item1,", "  item2,", "  item3", "]"]
        >>> collect_bracket_array(lines, 0, 0, "[")
        ("[item1, item2, item3]", 4, [(0, "item1", True), (1, "item2", True), (2, "item3", False)])
        
        >>> lines = ["  item1,", "  [", "    nested1,", "    nested2", "  ]", "  item3", "]"]
        >>> collect_bracket_array(lines, 0, 0, "[")
        ("[item1, [nested1, nested2], item3]", 7, [...])
    """
    collected_items = []
    item_line_info = []  # Track (line_idx, content, has_comma) for each item
    lines_consumed = 0

    # Determine the content indent level (first non-empty line's indent)
    content_indent = None
    for j in range(start_idx, len(lines)):
        test_line = lines[j].strip()
        if test_line and test_line != ']':
            content_indent = len(lines[j]) - len(lines[j].lstrip())
            break

    if content_indent is None:
        content_indent = parent_indent + 4  # Default fallback

    i = start_idx
    while i < len(lines):
        line = lines[i]
        line_indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Check if this is the closing bracket for THIS level
        # It should be at an indent <= content_indent (back-dedented from content)
        if stripped == ']':
            # Add closing bracket to item_line_info for token emission
            item_line_info.append((i, ']', False))
            lines_consumed += 1
            break

        if stripped.startswith(']'):
            # Add closing bracket to item_line_info for token emission
            item_line_info.append((i, ']', False))
            lines_consumed += 1
            break

        # Skip empty lines
        if not stripped:
            lines_consumed += 1
            i += 1
            continue

        # If line is dedented back to or past parent level, we might be done
        # (but ] should have been caught above)
        if line_indent < content_indent and stripped != '[':
            # This line is back-dedented - check if it's a closing bracket
            if ']' in stripped:
                break

        # Check if this is a nested array
        if stripped == '[' or stripped.startswith('['):
            # Check if array is complete on this line (balanced brackets)
            open_brackets = stripped.count('[') - stripped.count(']')
            
            if open_brackets == 0:
                # Single-line nested array - use as-is, just strip trailing comma
                has_comma = stripped.endswith(',')
                item_content = stripped.rstrip(',').strip()
                collected_items.append(item_content)
                item_line_info.append((i, item_content, has_comma))
                lines_consumed += 1
                i += 1
                continue
            
            # Multiline nested array - recursively collect
            # Add the opening bracket to item_line_info for token emission
            item_line_info.append((i, '[', False))

            # Recursively collect the nested array starting from NEXT line
            nested_reconstructed, nested_consumed, nested_info = collect_bracket_array(
                lines, i + 1, line_indent, '['
            )

            # Add the nested array as a single item for reconstruction
            collected_items.append(nested_reconstructed)

            # Add all nested items to item_line_info for token emission
            item_line_info.extend(nested_info)

            # Skip past the nested array content (nested_consumed already counted)
            lines_consumed += nested_consumed + 1  # +1 for the [ line itself
            i += nested_consumed + 1
            continue

        # Check if this is start of an inline object {...}
        if stripped == '{' or stripped.startswith('{'):
            # Check if object is complete on this line (balanced braces)
            open_braces = stripped.count('{') - stripped.count('}')
            
            if open_braces == 0:
                # Single-line inline object - use as-is, just strip trailing comma
                has_comma = stripped.endswith(',')
                item_content = stripped.rstrip(',').strip()
                collected_items.append(item_content)
                item_line_info.append((i, item_content, has_comma))
                lines_consumed += 1
                i += 1
                continue
            
            # Multiline inline object - collect all lines until matching }
            obj_lines = [stripped]
            obj_line_info = [(i, stripped, False)]  # Track each line for token emission

            lines_consumed += 1
            i += 1

            # Collect lines until braces are balanced
            while i < len(lines) and open_braces > 0:
                obj_line = lines[i]
                obj_stripped = obj_line.strip()

                if not obj_stripped:
                    lines_consumed += 1
                    i += 1
                    continue

                obj_lines.append(obj_stripped)
                has_comma = obj_stripped.endswith(',')
                obj_line_info.append((i, obj_stripped.rstrip(',').strip(), has_comma))

                open_braces += obj_stripped.count('{') - obj_stripped.count('}')
                lines_consumed += 1
                i += 1

            # Reconstruct as single inline object
            # Strip trailing comma ONLY from the closing brace line (last line)
            obj_content_lines = obj_lines[1:]  # All lines after opening {
            if obj_content_lines and obj_content_lines[-1].endswith(','):
                # Remove comma from closing brace: '},' -> '}'
                obj_content_lines[-1] = obj_content_lines[-1].rstrip(',').strip()

            # DON'T add closing } - it's already in obj_content_lines!
            reconstructed_obj = '{' + ' '.join(obj_content_lines)
            collected_items.append(reconstructed_obj)

            # Add all lines from this object to item_line_info for tokenization
            item_line_info.extend(obj_line_info)
            continue

        # Regular array item (single line)
        # Remove trailing comma if present
        has_comma = stripped.endswith(',')
        item_content = stripped.rstrip(',').strip()

        if item_content and item_content != ']':
            collected_items.append(item_content)
            item_line_info.append((i, item_content, has_comma))

        lines_consumed += 1
        i += 1

    # Reconstruct as single-line array format
    if collected_items:
        reconstructed = '[' + ', '.join(collected_items) + ']'
    else:
        reconstructed = '[]'

    return reconstructed, lines_consumed, item_line_info
