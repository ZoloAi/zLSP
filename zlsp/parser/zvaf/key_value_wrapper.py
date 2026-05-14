"""
zVaF Key-Value Wrapper - Adds modifier handling to basic key parsing

This module wraps core key_value_parser functions and adds zVaF-specific
modifier handling (^~*!) for dispatcher files (zUI, zEnv, zSpark).

Maintains separation of concerns:
- core/key_value_parser.py = basic YAML-like parsing
- zvaf/key_value_wrapper.py = zVaF-specific modifiers
"""

from typing import Tuple, Optional

from zlsp.lsp_types import Diagnostic, Range, Position
from zlsp.token_types import TokenType
from .modifier_handler import ModifierHandler, emit_key_with_modifiers
from .key_detector import KeyDetector
from .block_manager import enter_block_for_key, enter_nested_block_for_key

# Forward reference
TYPE_CHECKING = False
if TYPE_CHECKING:
    from ..core.token_emitter import TokenEmitter


def _parse_type_hint(key: str) -> Tuple[str, Optional[str], bool]:
    """
    Extract type hint from key if present.
    
    Delegates to centralized helper in basic/type_hints.py (SSOT).
    
    Args:
        key: Full key string (may include type hint)
    
    Returns:
        Tuple of (clean_key, type_hint, has_str_hint)
    """
    from ..basic.type_hints import extract_type_hint
    clean_key, type_hint = extract_type_hint(key)
    has_str_hint = type_hint is not None and type_hint.lower() == 'str'
    return clean_key, type_hint, has_str_hint


def _emit_type_hint(type_hint: Optional[str], clean_key: str, line_num: int,
                    key_start: int, emitter: 'TokenEmitter') -> None:
    """
    Emit type hint tokens if present (opening paren, hint text, closing paren).
    
    Args:
        type_hint: Type hint string or None
        clean_key: Key without type hint (used to calculate position)
        line_num: Line number for token emission
        key_start: Column position where key starts
        emitter: Token emitter instance
    """
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


def _validate_root_key(core_key: str, line_num: int, key_start: int,
                       emitter: 'TokenEmitter') -> bool:
    """
    Validate root-level keys and emit diagnostics for invalid ones.
    
    Delegates to centralized validator in basic/validators.py (SSOT).
    
    Args:
        core_key: Core key without modifiers
        line_num: Line number for diagnostics
        key_start: Column position where key starts
        emitter: Token emitter instance
        
    Returns:
        True if valid, False if invalid
    """
    from ..basic.validators import validate_root_key
    return validate_root_key(core_key, line_num, key_start, emitter.diagnostics)


def _parse_and_emit_key(
    key: str,
    line_num: int,
    key_start: int,
    indent: int,
    emitter: 'TokenEmitter',
    is_root: bool
) -> Tuple[str, Optional[str], bool]:
    """
    Core logic for parsing and emitting keys with modifiers.
    
    Args:
        key: Full key string (may include type hint and modifiers)
        line_num: Line number for token emission
        key_start: Column position where key starts
        indent: Current indentation level
        emitter: Token emitter instance
        is_root: True for root-level keys, False for nested keys
    
    Returns:
        Tuple of (clean_key, type_hint, has_str_hint)
    """
    # Parse type hint
    clean_key, type_hint, has_str_hint = _parse_type_hint(key)

    # Split modifiers to get core_key for token type detection
    _, core_key, _ = ModifierHandler.split_modifiers(clean_key)

    # Detect token type using KeyDetector
    if is_root:
        token_type = KeyDetector.detect_root_key(core_key, emitter, indent)
    else:
        token_type = KeyDetector.detect_nested_key(core_key, emitter, indent)

    # Emit key tokens with modifiers
    emit_key_with_modifiers(clean_key, line_num, key_start, token_type, emitter)

    # Emit type hint token if present
    _emit_type_hint(type_hint, clean_key, line_num, key_start, emitter)

    # Handle block entry and validation
    if is_root:
        is_valid = _validate_root_key(core_key, line_num, key_start, emitter)
        # Only enter block if valid root key
        if is_valid:
            enter_block_for_key(core_key, indent, line_num, emitter)
    else:
        enter_nested_block_for_key(core_key, indent, line_num, emitter)

    return clean_key, type_hint, has_str_hint


def parse_key_and_emit_root_zvaf(
    key: str,
    _line: str,
    line_num: int,
    key_start: int,
    indent: int,
    emitter: 'TokenEmitter'
) -> Tuple[str, Optional[str], bool]:
    """
    Parse root-level key with zVaF modifier handling.
    
    Splits modifiers (^~*!), emits tokens for each part, and delegates
    to KeyDetector for proper token type detection.
    
    Args:
        key: Full key string (may include type hint and modifiers)
        _line: Full line text (unused but kept for API consistency)
        line_num: Line number for token emission
        key_start: Column position where key starts
        indent: Current indentation level
        emitter: Token emitter instance
    
    Returns:
        Tuple of (clean_key, type_hint, has_str_hint)
    """
    # Clear ZNAVBAR and zMeta block tracking when we encounter a new root-level key
    emitter.znavbar_blocks = []
    emitter.zmeta_blocks = []

    return _parse_and_emit_key(key, line_num, key_start, indent, emitter, is_root=True)


def parse_key_and_emit_nested_zvaf(
    key: str,
    _line: str,
    line_num: int,
    key_start: int,
    indent: int,
    emitter: 'TokenEmitter'
) -> Tuple[str, Optional[str], bool]:
    """
    Parse nested key with zVaF modifier handling.
    
    Splits modifiers (^~*!), emits tokens for each part, and delegates
    to KeyDetector for proper token type detection.
    
    Args:
        key: Full key string (may include type hint and modifiers)
        _line: Full line text (unused but kept for API consistency)
        line_num: Line number for token emission
        key_start: Column position where key starts
        indent: Current indentation level
        emitter: Token emitter instance
    
    Returns:
        Tuple of (clean_key, type_hint, has_str_hint)
    """
    return _parse_and_emit_key(key, line_num, key_start, indent, emitter, is_root=False)
