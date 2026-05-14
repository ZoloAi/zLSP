"""
Pipe Multiline Collector

Collects multi-line string content after pipe | marker.
Preserves formatting and indentation within the content block.
"""

from typing import Tuple, Optional
from . import YAML_LINE_BREAK


def collect_pipe_multiline(
    lines: list[str],
    start_idx: int,
    parent_indent: int,
    parent_key: Optional[str] = None
) -> Tuple[str, int]:
    """
    Collect multi-line string content after pipe | marker.
    
    Args:
        lines: All lines
        start_idx: Index to start collecting from
        parent_indent: Indentation level of the parent key
        parent_key: The key name (used for semantic joining)
    
    Returns:
        Tuple of (multiline_string, lines_consumed)
    """
    collected = []
    base_indent = None
    lines_consumed = 0

    for i in range(start_idx, len(lines)):
        line = lines[i]
        line_indent = len(line) - len(line.lstrip())

        # If we hit a line at or less than parent indent, we're done
        if line and line_indent <= parent_indent:
            break

        # Set base indent from first content line
        if base_indent is None and line.strip():
            base_indent = line_indent

        # Collect line, stripping base indentation
        if base_indent is not None:
            if line_indent >= base_indent:
                # Strip base indent, keep relative indent
                relative_line = line[base_indent:] if len(line) >= base_indent else line.strip()
                collected.append(relative_line)
            else:
                collected.append(line.strip())
        else:
            collected.append(line.strip())

        lines_consumed += 1

    # Determine join character based on parent key
    clean_key = parent_key.split('__dup')[0].lower() if parent_key else None

    if clean_key == 'ztext':
        join_char = ' '
    elif clean_key == 'zmd':
        # zMD: Custom joining with code block awareness
        # Inside code blocks (```): always preserve newlines
        # Outside code blocks:
        #   - Lines ending with 2+ spaces → use \n (creates <br> in renderer)
        #   - Normal lines → use space (editor linebreaks are for readability)
        result = []
        in_code_block = False
        
        for i, line in enumerate(collected):
            # Check for code block markers (``` or ```language)
            stripped = line.strip()
            if stripped.startswith('```'):
                in_code_block = not in_code_block
            
            result.append(line)
            
            # Add separator if not the last line
            if i < len(collected) - 1:
                if in_code_block:
                    # Inside code block: always preserve newlines
                    result.append('\n')
                elif len(line) >= 2 and line[-2:] == '  ':
                    # Explicit line break with double space
                    result.append('\n')
                else:
                    # Normal line: join with space
                    result.append(' ')
        
        return ''.join(result), lines_consumed
    else:
        join_char = '\n'

    return join_char.join(collected), lines_consumed
