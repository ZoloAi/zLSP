"""
UI Shorthand Utilities - zVaF-Specific

Handles UI element shorthands (zText, zButton, zH1, etc.) used in zVaF files.
These are exempt from duplicate key checks because they represent sequences.
"""


def is_ui_event_shorthand(clean_key: str) -> bool:
    """
    Check if a key is a UI event shorthand element.
    
    UI event shorthands are exempt from duplicate key checks because they
    represent sequential UI elements, not dictionary keys.
    
    Uses centralized UI_ELEMENT_SHORTHAND_KEYS from token_registry.
    
    Examples: zText, zButton, zH1, zH2, etc.
    """
    from zlsp.token_registry import UI_ELEMENT_SHORTHAND_KEYS, ZRAVEN_REPEATABLE_KEYS
    return clean_key in UI_ELEMENT_SHORTHAND_KEYS or clean_key in ZRAVEN_REPEATABLE_KEYS


def handle_duplicate_ui_key(key: str, result: dict) -> str:
    """
    Generate a unique key for duplicate UI event shorthands.
    
    Returns:
        The original key if not a duplicate, or a suffixed key like "zText__dup2"
    """
    if key not in result:
        return key

    # Key already exists - add numeric suffix to preserve order
    counter = 2
    suffixed_key = f"{key}__dup{counter}"
    while suffixed_key in result:
        counter += 1
        suffixed_key = f"{key}__dup{counter}"
    return suffixed_key
