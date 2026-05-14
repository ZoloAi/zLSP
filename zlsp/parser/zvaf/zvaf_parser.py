"""
zVaF Line Parser

Wraps standard_parser with zVaF-specific extensions:
- Auto-multiline detection for UI properties (zText, zMD)
- UI shorthand support (zText, zButton can repeat)
"""

from .multiline_detection import check_auto_multiline_for_key
from ..core.line_parsers.dict_builder import build_nested_dict_zvaf
from ..core.line_parsers.standard_parser import parse_lines as parse_lines_basic


def parse_lines_zvaf(lines: list[str], line_mapping: dict = None) -> dict:
    """
    Parse lines with zVaF-specific features enabled.
    
    Extensions over basic parsing:
    - Auto-multiline: zText/zMD properties auto-enable multiline without (str) hint
    - UI shorthands: zText, zButton, etc. can appear multiple times in sequence
    
    Args:
        lines: Cleaned lines (from Step 1.1)
        line_mapping: Optional dict mapping cleaned line index to original line number (1-based)
    
    Returns:
        Nested dictionary with zVaF UI support
    
    Examples:
        >>> parse_lines_zvaf(["zText: Hello", "zText: World"])
        {'zText': 'Hello', 'zText__dup2': 'World'}
    """
    return parse_lines_basic(
        lines=lines,
        line_mapping=line_mapping,
        auto_multiline_checker=check_auto_multiline_for_key,
        dict_builder=build_nested_dict_zvaf
    )
