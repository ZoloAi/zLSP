"""
Key Classifications - Single Source of Truth for .zolo key categorization

This module provides centralized classification of keys by their semantic role:
- Block-level keys (expect nested properties, not inline values)
- UI element keys (zImage, zText, zH1-zH6, etc.)
- Structural keys (zSpark, zMachine, zServer, etc.)

Used by:
- Completion provider (to skip value completions for block keys)
- Hover provider (for context-aware documentation)
- Diagnostic formatter (for validation rules)
- Parser modules (for structure understanding)
"""

from typing import Set, Optional, List
from dataclasses import dataclass


# ============================================================================
# Block-Level Keys (Expect Nested Properties, NOT Inline Values)
# ============================================================================

# UI Element Keys - Represent visual components
UI_ELEMENT_KEYS: Set[str] = {
    # Basic elements
    'zImage', 'zText', 'zMD', 'zCode', 'zURL', 'zURLs', 'zTexts', 'zImages', 'zMDs',
    # Plural interactive elements
    'zBtns', 'zInputs', 'zCheckboxes', 'zSelects', 'zRanges', 'zIcons',
    # Plural headers
    'zH0s', 'zH1s', 'zH2s', 'zH3s', 'zH4s', 'zH5s', 'zH6s',
    
    # Headings
    'zH0', 'zH1', 'zH2', 'zH3', 'zH4', 'zH5', 'zH6',

    # Function calls
    'zFunc',
    
    # Lists and tables
    'zUL', 'zOL', 'zDL', 'zTable',
    
    # Interactive elements
    'zInput', 'zCheckbox', 'zBtn', 'zSelect', 'zRange',
    
    # Layout and navigation
    'zNavBar', 'zRBAC', 'zMeta',

    # Signal events
    'zSignal', 'zError', 'zWarning', 'zSuccess', 'zInfo',
}

# Structural Keys - Define application architecture
STRUCTURAL_KEYS: Set[str] = {
    # Top-level blocks
    'zSpark', 'zMachine', 'zServer', 'zCLI',
    
    # Data operation blocks
    'zData', 'zRead', 'zCreate', 'zUpdate', 'zDelete',
    
    # Schema definition blocks
    'zSchema', 'zFields',
}

# Container Keys - Child blocks that hold nested content
CONTAINER_KEYS: Set[str] = {
    'items', 'window', 'columns', 'rows', 'properties',
}

# All block-level keys combined
BLOCK_KEYS: Set[str] = UI_ELEMENT_KEYS | STRUCTURAL_KEYS | CONTAINER_KEYS


# ============================================================================
# UI Element Metadata (For Completions and Hover)
# ============================================================================

@dataclass
class UIElement:
    """
    Metadata for a UI element key.
    
    Used to generate completions and hover documentation.
    """
    label: str
    detail: str
    documentation: str
    insert_text: str
    category: str = "ui_element"
    priority: int = 0


# UI Elements with full metadata
UI_ELEMENTS: List[UIElement] = [
    # Basic elements
    UIElement(
        label="zImage",
        detail="Image element",
        documentation="Display an image. Expects properties like `src`, `alt`, `width`, `height`.",
        insert_text="zImage:\n    ",
        priority=1
    ),
    UIElement(
        label="zURL",
        detail="URL/Link",
        documentation="Single URL link. Use `href` and `text` properties.",
        insert_text="zURL:\n    ",
        priority=1
    ),
    UIElement(
        label="zURLs",
        detail="Multiple URLs",
        documentation="List of URL links with `items` property.",
        insert_text="zURLs:\n    items:\n        ",
        priority=1
    ),
    UIElement(
        label="zText",
        detail="Text element",
        documentation="Display text content. Use `content` or inline value.",
        insert_text="zText:\n    ",
        priority=1
    ),
    UIElement(
        label="zTexts",
        detail="Multiple texts",
        documentation="List of text items with `items` property.",
        insert_text="zTexts:\n    items:\n        ",
        priority=1
    ),
    UIElement(
        label="zImages",
        detail="Multiple images",
        documentation="Named group of image elements.",
        insert_text="zImages:\n    ",
        priority=1
    ),
    UIElement(
        label="zMDs",
        detail="Multiple markdown blocks",
        documentation="Named group of markdown content blocks.",
        insert_text="zMDs:\n    ",
        priority=1
    ),
    UIElement(
        label="zBtns",
        detail="Multiple buttons",
        documentation="Named group of button elements. Use _zClass inside for shared styling.",
        insert_text="zBtns:\n    _zClass: \n    ",
        priority=1
    ),
    UIElement(
        label="zInputs",
        detail="Multiple input fields",
        documentation="Named group of input elements.",
        insert_text="zInputs:\n    ",
        priority=1
    ),
    UIElement(
        label="zCheckboxes",
        detail="Multiple checkboxes",
        documentation="Named group of checkbox elements.",
        insert_text="zCheckboxes:\n    ",
        priority=1
    ),
    UIElement(
        label="zSelects",
        detail="Multiple select dropdowns",
        documentation="Named group of select elements.",
        insert_text="zSelects:\n    ",
        priority=1
    ),
    UIElement(
        label="zRanges",
        detail="Multiple range sliders",
        documentation="Named group of range/slider elements.",
        insert_text="zRanges:\n    ",
        priority=1
    ),
    UIElement(
        label="zIcons",
        detail="Multiple icons",
        documentation="Named group of icon elements.",
        insert_text="zIcons:\n    ",
        priority=1
    ),

    # Headings
    UIElement(
        label="zH0",
        detail="Heading 0 (display)",
        documentation="Display-level heading above h1, renders as <h1 class=\"zH0\">",
        insert_text="zH0: ",
        priority=1
    ),
    UIElement(
        label="zH1",
        detail="Heading 1",
        documentation="Large heading (highest level)",
        insert_text="zH1: ",
        priority=1
    ),
    UIElement(
        label="zH2",
        detail="Heading 2",
        documentation="Medium heading",
        insert_text="zH2: ",
        priority=1
    ),
    UIElement(
        label="zH3",
        detail="Heading 3",
        documentation="Small heading",
        insert_text="zH3: ",
        priority=1
    ),
    UIElement(
        label="zH4",
        detail="Heading 4",
        documentation="Smaller heading",
        insert_text="zH4: ",
        priority=1
    ),
    UIElement(
        label="zH5",
        detail="Heading 5",
        documentation="Tiny heading",
        insert_text="zH5: ",
        priority=1
    ),
    UIElement(
        label="zH6",
        detail="Heading 6",
        documentation="Smallest heading",
        insert_text="zH6: ",
        priority=1
    ),
    UIElement(
        label="zFunc",
        detail="Function call",
        documentation="Invoke a function or plugin method. Use & prefix for plugins.",
        insert_text="zFunc: ",
        priority=1
    ),

    # Lists
    UIElement(
        label="zUL",
        detail="Unordered list",
        documentation="Bullet list with `items` property",
        insert_text="zUL:\n    items:\n        ",
        priority=1
    ),
    UIElement(
        label="zOL",
        detail="Ordered list",
        documentation="Numbered list with `items` property",
        insert_text="zOL:\n    items:\n        ",
        priority=1
    ),
    UIElement(
        label="zDL",
        detail="Description list",
        documentation="Term-definition list with `items` property",
        insert_text="zDL:\n    items:\n        ",
        priority=1
    ),
    
    # Rich content
    UIElement(
        label="zMD",
        detail="Markdown",
        documentation="Markdown content block",
        insert_text="zMD: ",
        priority=1
    ),
    UIElement(
        label="zTable",
        detail="Table",
        documentation="Data table with `columns` and `rows` properties",
        insert_text="zTable:\n    columns:\n        ",
        priority=1
    ),
    
    # Layout
    UIElement(
        label="zNavBar",
        detail="Navigation bar",
        documentation="Enable/disable navigation bar (boolean value or config block)",
        insert_text="zNavBar: ",
        priority=1
    ),
]


# ============================================================================
# Classification Functions
# ============================================================================

def is_block_key(key: str) -> bool:
    """
    Check if a key is a block-level key (expects nested properties).
    
    Args:
        key: Key name to check
    
    Returns:
        True if key should not have inline values
    
    Examples:
        >>> is_block_key('zImage')
        True
        >>> is_block_key('title')
        False
    """
    return key in BLOCK_KEYS


def is_ui_element(key: str) -> bool:
    """
    Check if a key is a UI element.
    
    Args:
        key: Key name to check
    
    Returns:
        True if key is a UI element
    """
    return key in UI_ELEMENT_KEYS


def is_structural_key(key: str) -> bool:
    """
    Check if a key is a structural key (defines architecture).
    
    Args:
        key: Key name to check
    
    Returns:
        True if key is structural
    """
    return key in STRUCTURAL_KEYS


def get_ui_element(label: str) -> Optional[UIElement]:
    """
    Get UI element metadata by label.
    
    Args:
        label: Element label (e.g., 'zImage')
    
    Returns:
        UIElement metadata or None if not found
    """
    for element in UI_ELEMENTS:
        if element.label == label:
            return element
    return None


def get_ui_elements_by_category(category: str) -> List[UIElement]:
    """
    Get all UI elements in a category.
    
    Args:
        category: Category name
    
    Returns:
        List of UIElement objects
    """
    return [elem for elem in UI_ELEMENTS if elem.category == category]


# ============================================================================
# Export Public API
# ============================================================================

__all__ = [
    # Sets
    'BLOCK_KEYS',
    'UI_ELEMENT_KEYS',
    'STRUCTURAL_KEYS',
    'CONTAINER_KEYS',
    
    # Classes
    'UIElement',
    
    # Lists
    'UI_ELEMENTS',
    
    # Functions
    'is_block_key',
    'is_ui_element',
    'is_structural_key',
    'get_ui_element',
    'get_ui_elements_by_category',
]
