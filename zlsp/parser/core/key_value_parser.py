"""
Key-Value Parser - Parse key-value lines with token emission

Handles parsing of key-value lines, including:
- Type hint extraction
- Token emission for keys and values
- Diagnostic emission for invalid root keys

This is a BASIC layer - no zVaF-specific logic (modifiers, etc.)
"""

from typing import Tuple, Optional

from zlsp.lsp_types import Diagnostic, Range, Position
from zlsp.token_types import TokenType
from ..zvaf.key_detector import KeyDetector
from ..zvaf.block_manager import enter_block_for_key, enter_nested_block_for_key

# Forward reference
TYPE_CHECKING = False
if TYPE_CHECKING:
    from .token_emitter import TokenEmitter


def parse_key_and_emit_root(
    key: str,
    _line: str,
    line_num: int,
    key_start: int,
    indent: int,
    emitter: 'TokenEmitter'
) -> Tuple[str, Optional[str], bool]:
    """
    Parse root-level key and emit tokens (BASIC - no modifier handling).
    
    Args:
        key: Full key string (may include type hint)
        _line: Full line text (unused but kept for API consistency)
        line_num: Line number for token emission
        key_start: Column position where key starts
        indent: Current indentation level
        emitter: Token emitter instance
    
    Returns:
        Tuple of (clean_key, type_hint, has_str_hint)
    """
    # Extract type hint using centralized helper (SSOT in basic/type_hints.py)
    from ..basic.type_hints import extract_type_hint
    clean_key, type_hint = extract_type_hint(key)
    has_str_hint = type_hint is not None and type_hint.lower() == 'str'

    # Detect token type using KeyDetector (uses clean_key as-is, no modifier stripping)
    token_type = KeyDetector.detect_root_key(clean_key, emitter, indent)

    # Emit simple token for the key (no modifier splitting)
    emitter.emit(line_num, key_start, len(clean_key), token_type)

    # Emit type hint tokens if present (opening paren, hint text, closing paren)
    if type_hint:
        # Emit opening paren
        paren_pos = key_start + len(clean_key)
        emitter.emit(line_num, paren_pos, 1, TokenType.TYPE_HINT_PAREN)
        
        # Emit type hint text
        hint_start = paren_pos + 1
        emitter.emit(line_num, hint_start, len(type_hint), TokenType.TYPE_HINT)
        
        # Emit closing paren
        close_paren_pos = hint_start + len(type_hint)
        emitter.emit(line_num, close_paren_pos, 1, TokenType.TYPE_HINT_PAREN)

    # Validate root key and emit diagnostics if invalid (SSOT in validators.py)
    from ..basic.validators import validate_root_key
    is_valid = validate_root_key(clean_key, line_num, key_start, emitter.diagnostics)
    
    # Only enter block if valid root key
    if is_valid:
        enter_block_for_key(clean_key, indent, line_num, emitter)

    return clean_key, type_hint, has_str_hint


def parse_key_and_emit_nested(
    key: str,
    _line: str,
    line_num: int,
    key_start: int,
    indent: int,
    emitter: 'TokenEmitter'
) -> Tuple[str, Optional[str], bool]:
    """
    Parse nested key and emit tokens (BASIC - no modifier handling).
    
    Args:
        key: Full key string (may include type hint)
        _line: Full line text (unused but kept for API consistency)
        line_num: Line number for token emission
        key_start: Column position where key starts
        indent: Current indentation level
        emitter: Token emitter instance
    
    Returns:
        Tuple of (clean_key, type_hint, has_str_hint)
    """
    # Extract type hint using centralized helper (SSOT in basic/type_hints.py)
    from ..basic.type_hints import extract_type_hint
    clean_key, type_hint = extract_type_hint(key)
    has_str_hint = type_hint is not None and type_hint.lower() == 'str'

    # Detect token type using KeyDetector (uses clean_key as-is, no modifier stripping)
    token_type = KeyDetector.detect_nested_key(clean_key, emitter, indent)

    # Emit simple token for the key (no modifier splitting)
    emitter.emit(line_num, key_start, len(clean_key), token_type)

    # Emit type hint tokens if present (opening paren, hint text, closing paren)
    if type_hint:
        # Emit opening paren
        paren_pos = key_start + len(clean_key)
        emitter.emit(line_num, paren_pos, 1, TokenType.TYPE_HINT_PAREN)
        
        # Emit type hint text
        hint_start = paren_pos + 1
        emitter.emit(line_num, hint_start, len(type_hint), TokenType.TYPE_HINT)
        
        # Emit closing paren
        close_paren_pos = hint_start + len(type_hint)
        emitter.emit(line_num, close_paren_pos, 1, TokenType.TYPE_HINT_PAREN)

    # Check for block entry (UI elements, zRBAC, etc.)
    enter_nested_block_for_key(clean_key, indent, line_num, emitter)

    return clean_key, type_hint, has_str_hint


def should_enable_multiline_for_key(
    key: str,
    value: str,
    lines: list[str],
    current_idx: int,
    indent: int,
    emitter: 'TokenEmitter'
) -> bool:
    """
    Check if multiline should be enabled for this key.
    
    Delegates to KeyDetector.should_enable_auto_multiline() (SSOT).
    
    Args:
        key: Clean key name (without type hints, as-is from parser)
        value: Value on the same line (may be empty)
        lines: All lines being parsed
        current_idx: Current line index
        indent: Current line indent
        emitter: Token emitter with block context
    
    Returns:
        True if multiline should be enabled
    """
    # Delegate to centralized multiline detection (SSOT in key_detector.py)
    return KeyDetector.should_enable_auto_multiline(
        key, emitter, indent, value, lines, current_idx
    )
