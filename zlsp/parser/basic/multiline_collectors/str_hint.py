"""
String Hint Multiline Collector

Collects multi-line string content when (str) type hint is used (YAML-style).
Rule: Collect lines indented MORE than parent, strip base indent, preserve relative.
"""

from typing import Tuple, Optional
from . import YAML_LINE_BREAK


def collect_str_hint_multiline(
    lines: list[str],
    start_idx: int,
    parent_indent: int,
    first_value: str,
    parent_key: Optional[str] = None
) -> Tuple[str, int]:
    """
    Collect multi-line string content when (str) type hint is used (YAML-style).
    
    Rule: Collect lines indented MORE than parent, strip base indent, preserve relative.
    
    SEMANTIC JOINING based on parent_key:
    - 'ztext' or 'content' under ztext → Join with ' ' (space) for readability
    - 'zmd' or 'content' under zmd → Context-aware joining:
        * Inside code blocks (```): always '\n' (preserve formatting)
        * Lines ending with '  ' (2+ spaces): '\n' for <br>
        * Normal lines: ' ' (space, editor linebreaks are for readability)
    - Other keys → Join with '\n' (backward compatible)
    
    Args:
        lines: All lines
        start_idx: Index to start collecting from (line after the key)
        parent_indent: Indentation level of the parent key
        first_value: The value on the same line as the key (if any)
        parent_key: The key name (used for semantic joining)
    
    Returns:
        Tuple of (multiline_string, lines_consumed)
    
    Examples:
        >>> # zText: space-joined
        >>> lines = ["  continues", "  here"]
        >>> collect_str_hint_multiline(lines, 0, 0, "First", "zText")
        ("First continues here", 2)
        
        >>> # zMD: space-joined, unless line ends with double-space
        >>> lines = ["  continues", "  here"]
        >>> collect_str_hint_multiline(lines, 0, 0, "First", "zMD")
        ("First continues here", 2)
        
        >>> # zMD with double-space line break
        >>> lines = ["  continues  ", "  here"]
        >>> collect_str_hint_multiline(lines, 0, 0, "First", "zMD")
        ("First continues  \\nhere", 2)
    """
    collected = []

    # Add first value if present
    if first_value:
        collected.append(first_value)

    # Pre-compute clean_key so it's available inside the loop
    clean_key = parent_key.split('__dup')[0].lower() if parent_key else None

    base_indent = None
    lines_consumed = 0

    for i in range(start_idx, len(lines)):
        line = lines[i]
        line_indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Stop if line is at same or less indent than parent (unless empty)
        if stripped and line_indent <= parent_indent:
            break

        # Stop if this looks like a new key at the same level
        if stripped and ':' in stripped and line_indent <= parent_indent:
            break

        # Empty line - preserve it (will be joined with separator)
        if not stripped:
            collected.append('')
            lines_consumed += 1
            continue

        # Set base indent from first content line
        if base_indent is None:
            # When a key has an inline first_value and continuation lines are more
            # than one level deeper (e.g., `content: zVaF:\n        zText:`),
            # use parent_indent+4 as the strip base so nested structure is preserved.
            if first_value and line_indent > parent_indent + 4:
                base_indent = parent_indent + 4
            else:
                base_indent = line_indent

        # Strip base indent, keep relative (preserve trailing spaces for zMD double-space breaks)
        if base_indent is not None:
            if line_indent >= base_indent:
                relative_line = line[base_indent:] if len(line) >= base_indent else line.strip()
                collected.append(relative_line)
            else:
                collected.append(line.strip())
        else:
            collected.append(line.strip())

        lines_consumed += 1

    # Determine join character based on parent key (clean_key already computed above)
    if clean_key == 'ztext':
        # zText: Join with space for .zolo readability
        join_char = ' '
    elif clean_key == 'zmd':
        # zMD: Context-aware joining.
        # Prose continuation lines join with space (allows .zolo line-wrapping).
        # Block-level markdown elements (headings, list items, blockquotes, empty
        # lines) must stay on their own line — join with '\n'.
        result = []
        in_code_block = False

        def _is_block_marker(s: str) -> bool:
            """True when 's' is a markdown block-level line that needs its own line."""
            if not s:
                return True  # Empty line = paragraph break
            if s.startswith('#'):
                return True  # Heading
            if s.startswith('- ') or s.startswith('* ') or s.startswith('+ '):
                return True  # Unordered list item
            if s.startswith('> '):
                return True  # Blockquote
            # Ordered list item: digit(s) followed by '.' or ')'
            for j, ch in enumerate(s):
                if ch.isdigit():
                    continue
                if ch in '.)'  and j > 0:
                    return True
                break
            return False

        for i, line in enumerate(collected):
            stripped = line.strip()

            # Track code-block state
            if stripped.startswith('```'):
                in_code_block = not in_code_block

            result.append(line)

            if i < len(collected) - 1:
                next_stripped = collected[i + 1].strip()

                if in_code_block or next_stripped.startswith('```') or stripped.startswith('```'):
                    # Inside (or opening/closing) a code fence: always newline.
                    result.append('\n')
                elif len(line) >= 2 and line.endswith('  '):
                    # Explicit soft-break (double trailing space).
                    result.append('\n')
                elif _is_block_marker(stripped) or _is_block_marker(next_stripped):
                    # Block-level element on either side: must be on its own line.
                    result.append('\n')
                else:
                    # Plain prose continuation: space (preserves .zolo line-wrapping).
                    result.append(' ')

        return ''.join(result), lines_consumed
    elif clean_key == 'zcode':
        # zCode: preserve all newlines; the opening ```lang and closing ``` are
        # part of the fence shorthand — keep them so _parse_code_fence can strip them.
        return '\n'.join(collected), lines_consumed
    else:
        # Default: backward compatible newline joining
        join_char = '\n'

    return join_char.join(collected), lines_consumed
