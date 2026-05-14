"""
Block Manager - Consolidate block entry/exit logic

Handles entering and exiting UI element blocks (zRBAC, zImage, etc.)
"""

from zlsp.token_registry import (
    BLOCK_ZRBAC, BLOCK_ZIMAGE, BLOCK_ZTEXT, BLOCK_ZMD, BLOCK_ZURL,
    BLOCK_ZCRUMBS, BLOCK_HEADER, BLOCK_ZUL, BLOCK_ZTABLE, BLOCK_ZINPUT,
    BLOCK_ZCHECKBOX, BLOCK_ZBTN, BLOCK_ZSELECT, BLOCK_ZRANGE,
    BLOCK_ZMACHINE, BLOCK_ZSPARK, BLOCK_ZNAVBAR, BLOCK_ZMETA
)
from ..zvaf.key_detector import KeyDetector

# Forward reference
TYPE_CHECKING = False
if TYPE_CHECKING:
    from ..core.token_emitter import TokenEmitter


def update_all_blocks(indent: int, line_num: int, emitter: 'TokenEmitter') -> None:
    """
    Update all block tracking based on current indentation.
    
    Exits blocks we've left based on indentation level.
    Should be called for nested keys before processing.
    
    Args:
        indent: Current line's indentation level
        line_num: Current line number
        emitter: Token emitter with block tracking
    """
    emitter.update_blocks(indent, line_num)


def enter_block_for_key(core_key: str, indent: int, line_num: int, emitter: 'TokenEmitter') -> None:
    """
    Enter appropriate block based on key name.
    
    Uses centralized mapping from token_registry for data-driven block entry.
    
    Args:
        core_key: Clean key name (without modifiers or type hints)
        indent: Current indentation level
        line_num: Current line number
        emitter: Token emitter with block tracking
    """
    from zlsp.token_registry import UI_ELEMENT_MAPPING, SPECIAL_BLOCK_MAPPING
    
    # Check special blocks first (zRBAC, zMeta, ZNAVBAR, zMachine, zSpark)
    if core_key in SPECIAL_BLOCK_MAPPING:
        block_info = SPECIAL_BLOCK_MAPPING[core_key]
        block_type_const = block_info['block_type']
        method = block_info.get('method', 'enter_block')
        
        # Check file type restrictions
        if 'file_types' in block_info:
            if 'zschema' in block_info['file_types'] and not emitter.is_zschema_file:
                return
        
        # Call appropriate method
        if method == 'enter_block_single':
            emitter.enter_block_single(block_type_const, indent, line_num)
        else:
            emitter.enter_block(block_type_const, indent, line_num)
        return
    
    # Check UI element blocks
    if core_key in UI_ELEMENT_MAPPING:
        block_info = UI_ELEMENT_MAPPING[core_key]
        block_type_const = block_info.get('block_type')
        
        # Skip if no block type defined (e.g., zWizard, zOL)
        if block_type_const is None:
            return
        
        # Check if requires zUI file
        if block_info.get('requires_zui', False) and not emitter.is_zui_file:
            return
        
        emitter.enter_block(block_type_const, indent, line_num)


def enter_nested_block_for_key(core_key: str, indent: int, line_num: int, emitter: 'TokenEmitter') -> None:
    """
    Enter appropriate block for nested keys.
    
    Delegates to enter_block_for_key() since the logic is identical.
    Kept as separate function for API compatibility.
    
    Args:
        core_key: Clean key name (without modifiers or type hints)
        indent: Current indentation level
        line_num: Current line number
        emitter: Token emitter with block tracking
    """
    # Delegate to main function - logic is now centralized
    enter_block_for_key(core_key, indent, line_num, emitter)
