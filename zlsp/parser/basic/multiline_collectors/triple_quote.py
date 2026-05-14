"""
Triple Quote Multiline Collector

Collects multi-line string content between triple quotes.
Handles both single-line and multi-line triple-quoted strings.
"""

from typing import Tuple, Optional
from . import YAML_LINE_BREAK


def collect_triple_quote_multiline(
    lines: list[str],
    start_idx: int,
    initial_value: str,
    parent_key: Optional[str] = None
) -> Tuple[str, int]:
    '''
    Collect multi-line string content between triple quotes.
    
    Args:
        lines: All lines
        start_idx: Index of the line with opening triple-quotes
        initial_value: The value part (might contain opening and/or closing triple-quotes)
        parent_key: The key name (used for semantic joining)
    
    Returns:
        Tuple of (multiline_string, lines_consumed)
    '''
    # Check if it's all on one line: """content"""
    if initial_value.count('"""') >= 2:
        # Extract content between quotes
        content = initial_value.split('"""', 2)[1]
        return content, 0

    # Multi-line case: collect until closing """
    collected = []
    lines_consumed = 0

    # First line might have content after opening """
    first_line_content = initial_value[3:].strip()  # Remove opening """
    if first_line_content:
        collected.append(first_line_content)

    # Collect subsequent lines
    base_indent = None
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        lines_consumed += 1

        # Check for closing """
        if '"""' in line:
            # Get content before closing """
            closing_content = line.split('"""')[0]
            if base_indent is None and closing_content.strip():
                base_indent = len(line) - len(line.lstrip())
            if closing_content.strip():
                if base_indent is not None:
                    if len(closing_content) >= base_indent:
                        relative_line = closing_content[base_indent:]
                    else:
                        relative_line = closing_content.strip()
                    collected.append(relative_line.rstrip())
                else:
                    collected.append(closing_content.strip())
            break

        # Set base indent from first content line
        if base_indent is None and line.strip():
            base_indent = len(line) - len(line.lstrip())

        # Collect line, stripping base indentation
        if base_indent is not None:
            line_indent = len(line) - len(line.lstrip())
            if line_indent >= base_indent:
                relative_line = line[base_indent:] if len(line) >= base_indent else line.strip()
                collected.append(relative_line.rstrip())
            else:
                collected.append(line.strip())
        else:
            collected.append(line.rstrip())

    # Determine join character based on parent key
    clean_key = parent_key.split('__dup')[0].lower() if parent_key else None

    if clean_key == 'ztext':
        join_char = ' '
    elif clean_key == 'zmd':
        join_char = YAML_LINE_BREAK
    else:
        join_char = '\n'

    return join_char.join(collected), lines_consumed
