"""
Multiline Detection - zVaF-Specific

DEPRECATED: This module is now a thin wrapper around KeyDetector.should_enable_auto_multiline()
for backward compatibility. New code should use KeyDetector directly.
"""

import re
from typing import Optional

_KEY_LINE_RE = re.compile(
    r'^[A-Za-z_^~*!][A-Za-z0-9_\-^~*!]*(\([^)]*\))?\s*:'
)


def check_auto_multiline_for_key(
    key: str,
    value: str,
    indent: int,
    structured_lines: list[dict],
    lines: list[str],
    i: int
) -> tuple[bool, Optional[str]]:
    """
    Check if key should auto-enable multiline (for zText, zMD in UI blocks).
    
    DEPRECATED: Delegates to KeyDetector.should_enable_auto_multiline() (SSOT).
    This function is kept for backward compatibility with existing parsers.
    
    Returns:
        Tuple of (has_str_hint, parent_block_key)
    """
    # Note: This function requires an emitter to check block context,
    # but the old API doesn't provide one. For now, we do basic checks
    # without full block context awareness.
    
    # Clean key for checking
    clean_key = key.split('(')[0].strip()
    
    # Check if we're inside a UI element block by looking at previous lines
    if structured_lines:
        from zlsp.token_registry import AUTO_MULTILINE_PROPERTIES
        # Look backwards to find the parent UI element
        for prev_line in reversed(structured_lines):
            if prev_line['indent'] < indent:
                # This is a potential parent
                parent_key = prev_line['key'].split('(')[0].strip().lower()

                # Check if parent is a UI element and key is a multiline property
                if parent_key in AUTO_MULTILINE_PROPERTIES:
                    multiline_props = AUTO_MULTILINE_PROPERTIES[parent_key]
                    if clean_key.lower() in multiline_props:
                        return True, parent_key
                break  # Stop at first parent found

    # Check zText/zMD/zCode scalar shorthand with continuation
    if value and clean_key in ('zText', 'zMD', 'zCode') and i + 1 < len(lines):
        next_line = lines[i + 1]
        next_indent = len(next_line) - len(next_line.lstrip())
        next_stripped = next_line.strip()
        # Continuation if: more indented, not empty, doesn't look like a key
        is_likely_key = bool(_KEY_LINE_RE.match(next_stripped))
        if next_indent > indent and next_stripped and not is_likely_key:
            return True, clean_key.lower()

    return False, None
