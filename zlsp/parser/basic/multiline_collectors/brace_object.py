"""
Brace Object Collector

Collects multi-line object content from opening { to closing }.
Supports nested objects and inline arrays within objects.
"""

from typing import Tuple


def collect_brace_object(
    lines: list[str], start_idx: int, parent_indent: int, _first_value: str
) -> Tuple[str, int, list]:
    """
    Collect multi-line object content from opening { to closing }.
    
    SUPPORTS NESTED OBJECTS:
    - Recursively handles nested {nested_pairs} within objects
    - Properly tracks brace depth to find matching closing }
    
    Rules:
    - Opening { is on the key line (first_value = '{')
    - Collect lines indented MORE than parent
    - Stop when we find } that closes THIS object level
    - Track each pair's line number for token emission
    
    Args:
        lines: All lines
        start_idx: Index to start collecting from (line after opening {)
        parent_indent: Indentation level of the parent key with opening {
        _first_value: The value on the same line as the key (should be '{')
    
    Returns:
        Tuple of (reconstructed_object_string, lines_consumed, pair_line_info)
        - reconstructed_object_string: "{key1: val1, key2: val2, nested: {k: v}}"
        - lines_consumed: Number of lines consumed (NOT including opening {)
        - pair_line_info: List of (line_idx, pair_content, has_comma) for token emission
    
    Examples:
        >>> lines = ["  id: 42,", "  name: Bob,", "  active: true", "}"]
        >>> collect_brace_object(lines, 0, 0, "{")
        ("{id: 42, name: Bob, active: true}", 4, [(0, "id: 42", True), (1, "name: Bob", True), (2, "active: true", False)])
        
        >>> lines = ["  outer: value,", "  inner: {", "    nested: data", "  }", "}"]
        >>> collect_brace_object(lines, 0, 0, "{")
        ("{outer: value, inner: {nested: data}}", 5, [...])
    """
    collected_pairs = []
    pair_line_info = []  # Track (line_idx, content, has_comma) for each pair
    lines_consumed = 0

    # Determine the content indent level (first non-empty line's indent)
    content_indent = None
    for j in range(start_idx, len(lines)):
        test_line = lines[j].strip()
        if test_line and test_line != '}':
            content_indent = len(lines[j]) - len(lines[j].lstrip())
            break

    if content_indent is None:
        content_indent = parent_indent + 4  # Default fallback

    i = start_idx
    while i < len(lines):
        line = lines[i]
        line_indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Check if this is the closing brace for THIS level
        # It should be at an indent <= content_indent (back-dedented from content)
        if stripped == '}':
            # Add closing brace to pair_line_info for token emission
            pair_line_info.append((i, '}', False))
            lines_consumed += 1
            break

        if stripped.startswith('}'):
            # Add closing brace to pair_line_info for token emission
            pair_line_info.append((i, '}', False))
            lines_consumed += 1
            break

        # Skip empty lines
        if not stripped:
            lines_consumed += 1
            i += 1
            continue

        # If line is dedented back to or past parent level, we might be done
        # (but } should have been caught above)
        if line_indent < content_indent and stripped != '{':
            # This line is back-dedented - check if it's a closing brace
            if '}' in stripped:
                break

        # Check if this is a nested object opening
        if stripped == '{':
            # Add the opening brace to pair_line_info for token emission
            pair_line_info.append((i, '{', False))

            # Recursively collect the nested object starting from NEXT line
            nested_reconstructed, nested_consumed, nested_info = collect_brace_object(
                lines, i + 1, line_indent, '{'
            )

            # Add the nested object as a single pair value for reconstruction
            collected_pairs.append(nested_reconstructed)

            # Add all nested pairs to pair_line_info for token emission
            pair_line_info.extend(nested_info)

            # Skip past the nested object content (nested_consumed already counted)
            lines_consumed += nested_consumed + 1  # +1 for the { line itself
            i += nested_consumed + 1
            continue

        # Check if this is start of a multiline inline array [...]
        if stripped == '[' or stripped.startswith('['):
            # Collect all lines until matching ]
            arr_lines = [stripped]
            arr_line_info = [(i, stripped, False)]  # Track each line for token emission

            open_brackets = stripped.count('[') - stripped.count(']')
            lines_consumed += 1
            i += 1

            # Collect lines until brackets are balanced
            while i < len(lines) and open_brackets > 0:
                arr_line = lines[i]
                arr_stripped = arr_line.strip()

                if not arr_stripped:
                    lines_consumed += 1
                    i += 1
                    continue

                arr_lines.append(arr_stripped)
                has_comma = arr_stripped.endswith(',')
                arr_line_info.append((i, arr_stripped.rstrip(',').strip(), has_comma))

                open_brackets += arr_stripped.count('[') - arr_stripped.count(']')
                lines_consumed += 1
                i += 1

            # Reconstruct as single inline array
            # Strip trailing comma ONLY from the closing bracket line (last line)
            arr_content_lines = arr_lines[1:]  # All lines after opening [
            if arr_content_lines and arr_content_lines[-1].endswith(','):
                # Remove comma from closing bracket: '],' -> ']'
                arr_content_lines[-1] = arr_content_lines[-1].rstrip(',').strip()

            # DON'T add closing ] - it's already in arr_content_lines!
            reconstructed_arr = '[' + ' '.join(arr_content_lines)
            collected_pairs.append(reconstructed_arr)

            # Add all lines from this array to pair_line_info for tokenization
            pair_line_info.extend(arr_line_info)
            continue

        # Regular object pair (single line)
        # Remove trailing comma if present
        has_comma = stripped.endswith(',')
        pair_content = stripped.rstrip(',').strip()

        if pair_content and pair_content != '}' and ':' in pair_content:
            # Check if this is a key with inline nested object (e.g., "settings: {")
            colon_idx = pair_content.find(':')
            pair_value = pair_content[colon_idx+1:].strip()
            
            if pair_value == '{':
                # This is a nested object on the same line as the key
                # Add the key-value line to pair_line_info
                pair_line_info.append((i, pair_content, False))
                
                # Recursively collect the nested object starting from NEXT line
                nested_reconstructed, nested_consumed, nested_info = collect_brace_object(
                    lines, i + 1, line_indent, '{'
                )
                
                # Add the full key: {nested} as a single pair for reconstruction
                pair_key = pair_content[:colon_idx].strip()
                collected_pairs.append(f"{pair_key}: {nested_reconstructed}")
                
                # Add all nested pairs to pair_line_info for token emission
                pair_line_info.extend(nested_info)
                
                # Skip past the nested object content
                lines_consumed += nested_consumed + 1  # +1 for current line
                i += nested_consumed + 1
                continue
            else:
                # Regular key-value pair
                collected_pairs.append(pair_content)
                pair_line_info.append((i, pair_content, has_comma))

        lines_consumed += 1
        i += 1

    # Reconstruct as single-line object format
    if collected_pairs:
        reconstructed = '{' + ', '.join(collected_pairs) + '}'
    else:
        reconstructed = '{}'

    return reconstructed, lines_consumed, pair_line_info


# ============================================================================
# SECTION 4: Dash Lists
# ============================================================================