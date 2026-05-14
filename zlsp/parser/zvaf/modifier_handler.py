"""
Modifier Handler - zVaF-specific key modifier extraction and token emission

Handles dispatcher modifiers that only appear in zVaFiles (zUI, zEnv, zSpark):
- PREFIX: ^ (bounce), ~ (anchor)
- SUFFIX: * (menu), ! (required)

Provides both modifier extraction and token emission for complete modifier handling.
"""

from typing import Optional, TYPE_CHECKING

from zlsp.token_types import TokenType

if TYPE_CHECKING:
    from ..core.token_emitter import TokenEmitter


class ModifierHandler:
    """
    Handles extraction of zVaF-specific key modifiers.
    
    These modifiers are only found in zVaFiles (zUI, zEnv, zSpark) and are
    used by the Zolo dispatcher for special behaviors like menus, anchors, etc.
    """

    # Modifier character sets
    PREFIX_MODIFIERS = {'^', '~'}
    SUFFIX_MODIFIERS = {'*', '!'}

    @staticmethod
    def split_modifiers(key: str) -> tuple[str, str, str]:
        """
        Split key into prefix modifiers, core name, and suffix modifiers.
        
        Args:
            key: Full key string (may include modifiers)
        
        Returns:
            Tuple of (prefix_modifiers: str, core_key: str, suffix_modifiers: str)
        
        Examples:
            >>> ModifierHandler.split_modifiers('^logout')
            ('^', 'logout', '')
            >>> ModifierHandler.split_modifiers('~ZNAVBAR*')
            ('~', 'ZNAVBAR', '*')
            >>> ModifierHandler.split_modifiers('menu*!')
            ('', 'menu', '*!')
        """
        core_key = key
        prefix_mods = ""
        suffix_mods = ""

        # Extract prefix modifiers
        while core_key and core_key[0] in ModifierHandler.PREFIX_MODIFIERS:
            prefix_mods += core_key[0]
            core_key = core_key[1:]

        # Extract suffix modifiers
        while core_key and core_key[-1] in ModifierHandler.SUFFIX_MODIFIERS:
            suffix_mods = core_key[-1] + suffix_mods  # Prepend to maintain order
            core_key = core_key[:-1]

        return (prefix_mods, core_key, suffix_mods)

    @staticmethod
    def extract_modifiers(key: str) -> tuple[str, Optional[str], Optional[str]]:
        """
        Extract key modifiers and return with different signature for compatibility.
        
        NOTE: This is primarily for backwards compatibility with tests.
        For production code, prefer split_modifiers() which returns full modifier strings.
        
        Args:
            key: The full key name with potential modifiers
            
        Returns:
            Tuple of (core_key, prefix_modifier, suffix_modifier)
            Returns only the first character of each modifier set.
            
        Examples:
            >>> ModifierHandler.extract_modifiers('^locked')
            ('locked', '^', None)
            >>> ModifierHandler.extract_modifiers('editable!')
            ('editable', None, '!')
            >>> ModifierHandler.extract_modifiers('~default*')
            ('default', '~', '*')
        """
        prefix_mods, core_key, suffix_mods = ModifierHandler.split_modifiers(key)

        # Convert to optional format (None if empty)
        # Only return first character of each modifier set
        prefix_mod = prefix_mods[0] if prefix_mods else None
        suffix_mod = suffix_mods[0] if suffix_mods else None

        return (core_key, prefix_mod, suffix_mod)

    @staticmethod
    def is_zvaf_file(is_zui: bool, is_zenv: bool, is_zspark: bool) -> bool:
        """
        Check if file is a zVaF file type.
        
        Args:
            is_zui: Whether file is zUI type
            is_zenv: Whether file is zEnv type
            is_zspark: Whether file is zSpark type (currently disabled)
            
        Returns:
            True if any zVaF file type
        
        Note: zSpark temporarily disabled - will be rebuilt from scratch
        """
        return is_zui or is_zenv  # Removed is_zspark


def emit_key_with_modifiers(
    key: str,
    line_num: int,
    key_start: int,
    token_type: TokenType,
    emitter: 'TokenEmitter'
) -> None:
    """
    Emit tokens for key with modifiers.
    
    Single source of truth for modifier token emission.
    Splits key into: prefix_mods + core_key + suffix_mods
    Emits tokens in order, using purple color for modifiers in zEnv/zUI files.
    
    Args:
        key: Full key string (may include modifiers)
        line_num: Line number for token emission
        key_start: Column position where key starts
        token_type: Token type for the core key
        emitter: Token emitter instance
    """
    prefix_mods, core_key, suffix_mods = ModifierHandler.split_modifiers(key)
    current_pos = key_start

    # Emit prefix modifiers (purple in zEnv/zUI only)
    for _ in prefix_mods:
        if emitter.is_zenv_file or emitter.is_zui_file:
            emitter.emit(line_num, current_pos, 1, TokenType.ZRBAC_OPTION_KEY)
        current_pos += 1

    # Emit core key with specified token type
    emitter.emit(line_num, current_pos, len(core_key), token_type)
    current_pos += len(core_key)

    # Emit suffix modifiers (purple in zEnv/zUI only)
    for _ in suffix_mods:
        if emitter.is_zenv_file or emitter.is_zui_file:
            emitter.emit(line_num, current_pos, 1, TokenType.ZRBAC_OPTION_KEY)
        current_pos += 1
