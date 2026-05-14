"""
Indentation Validation

Validates that indentation is consistent throughout the file.
Allows either tabs OR spaces, but forbids mixing.
"""

from zlsp.exceptions import ZoloParseError
from ...basic.error_formatter import ErrorFormatter


def check_indentation_consistency(lines: list[str]) -> None:
    """
    Check that indentation is consistent (Python-style).
    
    Allows either tabs OR spaces for indentation, but forbids mixing.
    This is superior to YAML's arbitrary "spaces only" rule because:
    - Tabs are semantic (1 tab = 1 level)
    - Spaces are flexible (user choice)
    - Mixing is chaos (forbidden!)
    
    Args:
        lines: List of lines to check
    
    Raises:
        ZoloParseError: If tabs and spaces are mixed in indentation
    
    Philosophy:
        Like Python, .zolo cares about CONSISTENCY, not character type.
        Choose tabs (semantic) OR spaces (traditional), but be consistent!
    
    TODO (low priority): Consider enforcing 4-space standard for consistency.
        Currently allows any space count. Could validate indent multiples match
        a detected base unit (2, 4, etc.). For now, use .editorconfig to guide IDEs.
    """
    first_indent_type = None  # 'tab' or 'space'
    first_indent_line = None

    for line_num, line in enumerate(lines, 1):
        # Skip empty lines and lines with no indentation
        if not line.strip():
            continue

        # Get indentation characters
        stripped = line.lstrip()
        if len(stripped) == len(line):
            # No indentation
            continue

        indent_chars = line[:len(line) - len(stripped)]

        # Check what this line uses
        has_tab = '\t' in indent_chars
        has_space = ' ' in indent_chars

        # ERROR: Mixed tabs and spaces in SAME line
        if has_tab and has_space:
            raise ZoloParseError(
                f"Mixed tabs and spaces in indentation at line {line_num}.\n"
                f"Use either tabs OR spaces consistently (Python convention).\n"
                f"Hint: Configure your editor to use one type of indentation."
            )

        # Determine this line's indent type
        current_type = 'tab' if has_tab else 'space'

        # Track first indent type seen in file
        if first_indent_type is None:
            first_indent_type = current_type
            first_indent_line = line_num
        # ERROR: Different type than rest of file
        elif first_indent_type != current_type:
            error_msg = ErrorFormatter.format_indentation_error(
                line_num=line_num,
                expected_type=first_indent_type,
                actual_type=current_type,
                first_indent_line=first_indent_line
            )
            raise ZoloParseError(error_msg)
