"""
Key Detector - Context-aware key type detection

Detects special keys and determines their token types based on file type,
indentation, and block context. Centralizes key detection logic that was
previously scattered across line_parsers.py.
"""

import re
from typing import Optional, TYPE_CHECKING
from zlsp.token_types import TokenType

# Shared key-line pattern (same definition as multiline_token_handlers._KEY_LINE_RE)
_KEY_LINE_RE = re.compile(
    r'^[A-Za-z_^~*!][A-Za-z0-9_\-^~*!]*(\([^)]*\))?\s*:'
)
from zlsp.token_registry import (
    ZOS_DATA_KEYS,
    ZSCHEMA_PROPERTY_KEYS,
    CONTROL_FLOW_KEYS,
    UI_ELEMENT_PROPERTY_KEYS,
    DISPATCH_KEYS,
    AUTO_MULTILINE_PROPERTIES,
    ZENV_CONFIG_ROOT_KEYS,
    ZMACHINE_LOCKED_SECTIONS,
    ZMACHINE_EDITABLE_SECTIONS,
    UI_ELEMENT_BLOCK_TYPES,
)

if TYPE_CHECKING:
    from ..core.token_emitter import TokenEmitter


class KeyDetector:
    """
    Context-aware key detector for special .zolo file types.
    
    Detects special keys and determines their semantic token types based on:
    - File type (zSpark, zEnv, zUI, zConfig, zSchema)
    - Key name and patterns
    - Indentation level
    - Block nesting context
    - Key modifiers (^, ~, !, *)
    
    Provides a single source of truth for key classification across all file types.
    
    Note: Key sets are now imported from token_registry for centralized management.
    """



    @staticmethod
    def detect_root_key(
        key: str,
        emitter: 'TokenEmitter',
        _indent: int
    ) -> TokenType:
        """
        Detect token type for root-level keys.
        
        Args:
            key: The key name (without modifiers)
            emitter: TokenEmitter with file type context
            _indent: Current indentation level (unused, for API compatibility)
            
        Returns:
            Appropriate TokenType for the key
        """
        # zMeta in zUI or zSchema files (GREEN)
        if (emitter.is_zui_file and (key == 'zMeta' or key == 'zVaF' or key == emitter.zui_component_name)) or \
           (emitter.is_zschema_file and key == 'zMeta'):
            return TokenType.ZMETA_KEY

        # zSpark root key in zSpark files (LIGHT GREEN - ANSI 114)
        # DISABLED: zSpark being rebuilt from scratch
        # if emitter.is_zspark_file and key == 'zSpark':
        #     return TokenType.ZSPARK_KEY

        # Config root keys in zEnv files (PURPLE - ANSI 98)
        if emitter.is_zenv_file and key in ZENV_CONFIG_ROOT_KEYS:
            return TokenType.ZENV_CONFIG_KEY

        # Uppercase Z-prefixed config keys in zEnv files (GREEN)
        if emitter.is_zenv_file and key.isupper() and key.startswith('Z'):
            return TokenType.ZCONFIG_KEY

        # zMachine root key in zConfig files (LIGHT GREEN - ANSI 114)
        if emitter.is_zconfig_file and key == 'zMachine':
            return TokenType.ZCONFIG_KEY

        # Uppercase Z-prefixed keys in zConfig files (e.g., ZPREFERENCES)
        if emitter.is_zconfig_file and key.isupper() and key.startswith('Z'):
            return TokenType.ZCONFIG_KEY

        # zConfig root key from filename (e.g., zMachine) in zConfig files (GREEN)
        if emitter.is_zconfig_file and key == emitter.zconfig_component_name:
            return TokenType.ZCONFIG_KEY

        # Default root key
        return TokenType.ROOT_KEY

    @staticmethod
    def detect_nested_key(
        key: str,
        emitter: 'TokenEmitter',
        indent: int
    ) -> TokenType:
        """
        Detect token type for nested keys.
        
        Args:
            key: The key name (without modifiers)
            emitter: TokenEmitter with file type and block context
            indent: Current indentation level
            
        Returns:
            Appropriate TokenType for the key
        """
        # zSpark nested keys (in zSpark files) - all nested keys under zSpark: root (LAVENDER)
        # DISABLED: zSpark being rebuilt from scratch
        # if emitter.is_zspark_file and emitter.is_inside_block('zSpark', indent):
        #     # All keys under zSpark: should be lavender (title, zState, zScrap, zMode, etc.)
        #     return TokenType.ZSPARK_NESTED_KEY

        # zConfig hierarchical keys (in zConfig files)
        if emitter.is_zconfig_file and emitter.is_inside_block('zMachine', indent):
            # Level 1 (indent == 1): Section headers (machine_identity, user_preferences, etc.)
            # Note: Parser counts indent levels, not spaces/tabs (1 tab = 1 level, 4 spaces = 1 level)
            if indent == 1:
                if key in ZMACHINE_LOCKED_SECTIONS:
                    return TokenType.ZMACHINE_LOCKED_KEY  # RED
                elif key in ZMACHINE_EDITABLE_SECTIONS:
                    return TokenType.ZMACHINE_EDITABLE_KEY  # BLUE
                # Default to NESTED_KEY if not in either set
                return TokenType.NESTED_KEY

            # Level 2+ (indent >= 2): Property keys under sections (os, browser, etc.)
            elif indent >= 2:
                return TokenType.ZCONFIG_NESTED_KEY  # LAVENDER

        # zRBAC key (TOMATO RED - ANSI 196)
        if key == 'zRBAC' and (emitter.is_zenv_file or emitter.is_zui_file):
            return TokenType.ZRBAC_KEY

        # zRBAC option keys (PURPLE 98)
        if emitter.is_inside_block('zRBAC', indent):
            ZRBAC_OPTION_KEYS = {'access', 'role', 'permissions', 'owner', 'public', 'private'}
            if key in ZRBAC_OPTION_KEYS:
                return TokenType.ZRBAC_OPTION_KEY

        # ZNAVBAR first-level nested keys (ANSI 208 in zEnv files)
        if emitter.is_first_level_in_block('ZNAVBAR', indent) and emitter.is_zenv_file:
            return TokenType.ZNAVBAR_NESTED_KEY

        # zOS zData keys under zMeta in zSchema files (PURPLE 98)
        if emitter.is_first_level_in_block('zMeta', indent) and emitter.is_zschema_file:
            if key in ZOS_DATA_KEYS:
                return TokenType.ZOS_DATA_KEY

        # zSchema property keys (PURPLE 98)
        if emitter.is_zschema_file and not emitter.is_first_level_in_block('zMeta', indent):
            # Check if we're inside a field definition (grandchild+ level)
            if indent >= 4 and key in ZSCHEMA_PROPERTY_KEYS:
                return TokenType.ZSCHEMA_PROPERTY_KEY

        # zSub key (purple 98 when grandchild+ in zEnv/zUI files)
        if key == 'zSub':
            if (emitter.is_zenv_file or emitter.is_zui_file) and indent >= 4:
                return TokenType.ZSUB_KEY
            else:
                return TokenType.UI_ELEMENT_KEY

        # Bifrost keys (underscore-prefixed)
        if key.startswith('_'):
            return TokenType.BIFROST_KEY

        # zRaven-only test primitive keys — silver-white
        _ZRAVEN_PRIMITIVE_KEYS = {'zPick', 'zSubmit', 'zAssert', 'zBoot', 'zExecute',
                                   'zWait', 'zClick', 'zType', 'zShot', 'zDrag', 'zMarker'}
        if emitter.is_zui_file and key in _ZRAVEN_PRIMITIVE_KEYS:
            filename = getattr(emitter, 'filename', '') or ''
            if 'zRaven.' in filename:
                return TokenType.ZRAVEN_PICK_KEY

        # Control flow construct keys (zWizard)
        if emitter.is_zui_file and key in CONTROL_FLOW_KEYS:
            return TokenType.CONTROL_FLOW_KEY

        # zDispatch event keys (zDialog, zData, zCRUD, zLogin) — golden
        if emitter.is_zui_file and key in DISPATCH_KEYS:
            return TokenType.DISPATCH_KEY

        # UI element keys - use mapping for centralized detection
        from zlsp.token_registry import UI_ELEMENT_MAPPING
        if key in UI_ELEMENT_MAPPING:
            block_info = UI_ELEMENT_MAPPING[key]
            if block_info.get('requires_zui', False):
                if emitter.is_zui_file:
                    return TokenType.UI_ELEMENT_KEY
            else:
                return TokenType.UI_ELEMENT_KEY

        # zShot / zRaven primitive property keys — lavender, no block-context check needed
        _ZRAVEN_PROP_KEYS = {
            'full_page', 'resolution', 'quality', 'selector', 'delay',
            'overwrite', 'burst', 'every', 'count',
        }
        filename = getattr(emitter, 'filename', '') or ''
        if 'zRaven.' in filename and key in _ZRAVEN_PROP_KEYS:
            return TokenType.UI_ELEMENT_PROPERTY_KEY

        # UI element property keys (src, etc.) inside UI elements
        if emitter.is_zui_file and key in UI_ELEMENT_PROPERTY_KEYS:
            # Check if we're inside any UI element block
            for block_type in UI_ELEMENT_BLOCK_TYPES:
                if emitter.is_inside_block(block_type, indent):
                    return TokenType.UI_ELEMENT_PROPERTY_KEY

        # Default nested key
        return TokenType.NESTED_KEY

    @staticmethod
    def extract_modifiers(key: str) -> tuple[str, Optional[str], Optional[str]]:
        """
        Extract key modifiers (^, ~, !, *) from a key name.
        
        DEPRECATED: Use ModifierHandler.extract_modifiers() instead.
        This method is kept for backward compatibility.
        
        Args:
            key: The full key name with potential modifiers
            
        Returns:
            Tuple of (core_key, prefix_modifier, suffix_modifier)
            
        Examples:
            >>> extract_modifiers('^locked')
            ('locked', '^', None)
            >>> extract_modifiers('editable!')
            ('editable', None, '!')
            >>> extract_modifiers('~default*')
            ('default', '~', '*')
        """
        from .modifier_handler import ModifierHandler
        return ModifierHandler.extract_modifiers(key)

    @staticmethod
    def should_enter_block(key: str, emitter: 'TokenEmitter') -> Optional[str]:
        """
        Determine if a key should trigger entering a block context.
        
        Uses UI_ELEMENT_MAPPING and SPECIAL_BLOCK_MAPPING from token_registry.
        
        Args:
            key: The key name (without modifiers)
            emitter: TokenEmitter with file type context
            
        Returns:
            Block type name if should enter, None otherwise
        """
        from zlsp.token_registry import UI_ELEMENT_MAPPING, SPECIAL_BLOCK_MAPPING
        
        # Check special blocks (zRBAC, zMeta, ZNAVBAR, zMachine, zSpark)
        if key in SPECIAL_BLOCK_MAPPING:
            block_info = SPECIAL_BLOCK_MAPPING[key]
            # Check file type restrictions
            if 'file_types' in block_info:
                if 'zschema' in block_info['file_types'] and not emitter.is_zschema_file:
                    return None
            return block_info['block_name']
        
        # Check UI element blocks
        if key in UI_ELEMENT_MAPPING:
            block_info = UI_ELEMENT_MAPPING[key]
            # Check if requires zUI file
            if block_info.get('requires_zui', False) and not emitter.is_zui_file:
                return None
            return block_info['block_name']
        
        return None

    @staticmethod
    def should_enable_auto_multiline(
        key: str,
        emitter: 'TokenEmitter',
        current_indent: int,
        value: str = '',
        lines: list = None,
        current_idx: int = 0
    ) -> bool:
        """
        Check if a property should automatically enable multiline mode.

        Single source of truth for multiline detection across all parsers.

        Args:
            key: The property key name (without type hint)
            emitter: TokenEmitter with block context
            current_indent: Current indentation level
            value: Optional inline value (for scalar shorthand detection)
            lines: Optional lines list (for continuation detection)
            current_idx: Optional current line index

        Returns:
            True if this property should auto-enable multiline (no (str): needed)
        """
        # Check each UI element type to see if we're inside one
        for block_type, multiline_props in AUTO_MULTILINE_PROPERTIES.items():
            if emitter.is_inside_block(block_type, current_indent):
                # Check if this key is a multiline property for this block type
                if key.lower() in multiline_props:
                    return True
        
        # Check zText/zMD scalar shorthand with continuation
        # Enables: zText: First line
        #              continuation line (space-joined for zText)
        if value and key in ('zText', 'zMD', 'zCode') and lines is not None:
            if current_idx + 1 < len(lines):
                next_line = lines[current_idx + 1]
                next_indent = len(next_line) - len(next_line.lstrip())
                next_stripped = next_line.strip()
                # Continuation if: more indented, not empty, doesn't look like a key
                is_likely_key = bool(_KEY_LINE_RE.match(next_stripped))
                if next_indent > current_indent and next_stripped and not is_likely_key:
                    return True

        # FALLBACK: Check if this is content/label under zMD/zText (matches comment processor logic)
        # This handles cases where zMD/zText are used in non-zUI files or before block tracking
        if key.lower() in ('content', 'label') and lines is not None and current_idx > 0:
            # Look back to find parent key
            for prev_idx in range(current_idx - 1, -1, -1):
                prev_line = lines[prev_idx]
                prev_indent = len(prev_line) - len(prev_line.lstrip())
                prev_stripped = prev_line.lstrip()
                
                # Found a parent at less indentation
                if prev_indent < current_indent and prev_stripped and ':' in prev_stripped:
                    parent_key = prev_stripped.split(':')[0].strip().lower()
                    # Strip type hints from parent key
                    if '(' in parent_key:
                        parent_key = parent_key.split('(')[0].strip()
                    
                    # If parent is zMD or zText, enable multiline for content/label
                    if parent_key in ('zmd', 'ztext', 'zcode'):
                        return True
                    break

        return False


# Helper functions for backward compatibility
def detect_key_type(
    key: str,
    emitter: 'TokenEmitter',
    indent: int,
    is_root: bool = False
) -> TokenType:
    """
    Convenience function to detect key type.
    
    Args:
        key: The key name (without modifiers)
        emitter: TokenEmitter with file type and block context
        indent: Current indentation level
        is_root: Whether this is a root-level key
        
    Returns:
        Appropriate TokenType for the key
    """
    if is_root:
        return KeyDetector.detect_root_key(key, emitter, indent)
    else:
        return KeyDetector.detect_nested_key(key, emitter, indent)
