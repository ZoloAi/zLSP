"""
Validators - Pure validation functions

No dependencies, just validation logic.
"""

from typing import TYPE_CHECKING, Optional
from zlsp.exceptions import ZoloParseError

if TYPE_CHECKING:
    from zlsp.lsp_types import Diagnostic


def validate_ascii_only(value: str, line_num: int = None, strict: bool = True) -> None:
    """
    Validate that value contains only ASCII characters (RFC 8259 compliance).
    
    Non-ASCII characters (emojis, accented letters, etc.) are detected and
    a helpful error message suggests the proper Unicode escape format.
    
    This provides error-driven education:
    - User can naturally type/paste emojis: icon: ♥️
    - Parser catches it and suggests: icon: \\u2764\\uFE0F
    - User learns the RFC 8259 compliant format
    - No IDE integration needed!
    
    Args:
        value: String value to validate
        line_num: Optional line number for error messages
        strict: If False, skip validation (allow emojis for LSP-level hints)
    
    Raises:
        ZoloParseError: If non-ASCII characters are detected and strict=True
    
    Examples:
        >>> validate_ascii_only("hello")  # OK
        >>> validate_ascii_only("♥️")  # Raises error with suggestion (if strict=True)
        >>> validate_ascii_only("♥️", strict=False)  # OK (LSP will hint instead)
    """
    # Allow emojis if not in strict mode (LSP provides INFO hints instead)
    if not strict:
        return

    for char in value:
        if ord(char) > 127:  # Non-ASCII detected
            # Convert character to Unicode escape sequence
            codepoint = ord(char)

            if codepoint <= 0xFFFF:
                # Basic Multilingual Plane (most characters)
                escape = f"\\u{codepoint:04X}"
            else:
                # Supplementary plane (emojis, etc.) - use \UXXXXXXXX format
                # This is cleaner than surrogate pairs for emojis
                escape = f"\\U{codepoint:08X}"

            # Get character name for better error message
            char_name = None
            try:
                import unicodedata
                char_name = unicodedata.name(char, None)
            except Exception:
                pass

            # Build helpful error message
            line_info = f" at line {line_num}" if line_num else ""
            char_desc = f" ({char_name})" if char_name else ""

            error_msg = (
                f"Non-ASCII character '{char}' detected{line_info}.\n"
                f"Unicode: U+{codepoint:04X}{char_desc}\n"
                f"\n"
                f"RFC 8259 requires ASCII-only. Use Unicode escape instead:\n"
                f"  {escape}\n"
                f"\n"
                f"Hint: Copy the escape sequence above and replace the character.\n"
                f"      This teaches you the RFC 8259 compliant format!"
            )

            raise ZoloParseError(error_msg)


def is_zpath_value(value: str) -> bool:
    """
    Check if value is a zPath (zOS path resolution syntax).
    
    zPath format:
    - Starts with @ or ~ modifier
    - Can be bare @ or ~ (refers to root)
    - Or followed by dot-separated path components
    - Examples: @, ~, @.static.brand.logo.png, ~.config.theme
    
    Args:
        value: String to check
    
    Returns:
        True if valid zPath, False otherwise
    """
    if not value:
        return False

    # Must start with @ or ~
    if value[0] not in ('@', '~'):
        return False

    # Bare @ or ~ is valid (refers to root)
    if len(value) == 1:
        return True

    # If longer, must have dot after modifier
    if value[1] != '.':
        return False

    # Must have at least one path component after the first dot
    if len(value) < 3:
        return False

    return True


def is_env_config_value(value: str) -> bool:
    """
    Check if value is an environment/configuration constant.
    
    Detects configuration states in two patterns:
    1. ALL-CAPS: PROD, DEBUG, INFO, ENABLED, etc.
    2. Mixed-case deployment terms: Development, Production, Staging, etc.
    
    Args:
        value: String to check
    
    Returns:
        True if value matches env/config pattern, False otherwise
    """
    if not value or len(value) < 2:
        return False

    # Must be alphabetic only (no numbers, no special chars)
    if not value.isalpha():
        return False

    # Check mixed-case deployment/environment terms first (case-insensitive)
    DEPLOYMENT_TERMS = {
        'development', 'production', 'staging', 'testing', 'debug',
        'local', 'remote', 'beta', 'alpha', 'release'
    }

    if value.lower() in DEPLOYMENT_TERMS:
        return True

    # Must be all uppercase for other constants
    if not value.isupper():
        return False

    # Whitelist of common ALL-CAPS environment/config constants
    ENV_CONSTANTS = {
        # Log levels
        'PROD', 'DEBUG', 'SESSION', 'INFO', 'WARN', 'WARNING', 'ERROR', 'CRITICAL', 'TRACE', 'FATAL',
        # Environments
        'DEV', 'DEVELOPMENT', 'STAGING', 'PRODUCTION', 'TEST', 'LOCAL',
        # States
        'ENABLED', 'DISABLED', 'ACTIVE', 'INACTIVE', 'ON', 'OFF',
        'YES', 'NO',
        # Modes
        'STRICT', 'PERMISSIVE', 'NORMAL', 'VERBOSE', 'QUIET', 'SILENT',
    }

    return value in ENV_CONSTANTS


def is_valid_number(value: str) -> bool:
    r"""
    Check if value is a valid RFC 8259 number.
    
    Rules:
    - Must match: -?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?
    - Anti-quirk: NO leading zeros (except '0' or '0.x')
    
    Valid:
        5000, -42, 0, 30.5, 1.5e10, 2E-3, 0.5
    
    Invalid (Anti-Quirk):
        00123 (leading zero), 01 (leading zero), 1.0.0 (multiple dots)
    
    Prism Regex Equivalent:
        -?(?:0(?!\d)|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?
        Used by: value_pattern_generator.py for syntax highlighting
    
    Args:
        value: String to check
    
    Returns:
        True if valid number, False otherwise
    """
    if not value:
        return False

    # Anti-quirk: Check for leading zeros (except '0' or '0.something')
    if len(value) > 1 and value[0] == '0' and value[1].isdigit():
        # This is like '00123' or '01' - NOT a valid number
        return False

    # Try to parse as float
    try:
        float(value)
        return True
    except ValueError:
        return False


# =============================================================================
# Root Key Validation (SSOT)
# =============================================================================

# Invalid root keys with their error messages (SINGLE SOURCE OF TRUTH)
INVALID_ROOT_KEYS = {
    'zSub': "'zSub' cannot be at root level. It must be nested under a parent key.",
    'zGate': "'zGate' cannot be at root level. It must be nested under a parent key.",
    'zRBAC': "'zRBAC' cannot be at root level. It must be nested under a parent key.",
}


def validate_root_key(core_key: str, line_num: int, key_start: int, 
                      diagnostics: Optional[list] = None) -> bool:
    """
    Validate that a key is allowed at root level.
    
    Single source of truth for root key validation. Emits diagnostic if invalid.
    
    Args:
        core_key: Core key without modifiers
        line_num: Line number for diagnostics
        key_start: Column position where key starts
        diagnostics: Optional list to append diagnostic to
        
    Returns:
        True if valid, False if invalid
    """
    if core_key in INVALID_ROOT_KEYS:
        if diagnostics is not None:
            from zlsp.lsp_types import Diagnostic, Range, Position
            error_range = Range(
                Position(line_num, key_start),
                Position(line_num, key_start + len(core_key))
            )
            diagnostic = Diagnostic(
                range=error_range,
                message=INVALID_ROOT_KEYS[core_key],
                severity=1
            )
            diagnostics.append(diagnostic)
        return False
    return True
