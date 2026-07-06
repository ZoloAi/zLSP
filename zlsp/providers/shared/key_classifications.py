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
    'zNavBar', 'zGate', 'zRBAC', 'zMeta',
    'zLink', 'zCrumbs',

    # Navigation verbs (doc 14)
    'zAlpha', 'zDelta', 'zOmega', 'zPsi', 'zDelegate',

    # Media events (doc 08)
    'zVideo', 'zEmbed',

    # Rich-UI events (docs 22–25) + wizard/terminal
    'zSwiper', 'zDash', 'zProgress', 'zTerminal', 'zWizard',

    # Dispatch display events (treated as block UI elements)
    'zMenu',

    # Export / Import events
    'zExport',
    'zImport',

    # Signal events
    'zSignal', 'zError', 'zWarning', 'zSuccess', 'zInfo', 'zPrimary', 'zSecondary',
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

    # Media (doc 08)
    UIElement(
        label="zVideo",
        detail="Video clip",
        documentation="Own video file with native controls. Keys: src (required), alt_text, caption, poster, loop, muted, autoplay, _zClass.",
        insert_text="zVideo:\n    src: \n    alt_text: ",
        priority=1
    ),
    UIElement(
        label="zEmbed",
        detail="Embedded outside media",
        documentation="Embed an external provider (YouTube/Vimeo/Spotify/Maps) from its normal link. Keys: src (required), alt_text, caption, _zClass. Provider allow-list via ZEMBED_MODE.",
        insert_text="zEmbed:\n    src: \n    alt_text: ",
        priority=1
    ),

    # Rich UI (docs 22, 23, 25)
    UIElement(
        label="zSwiper",
        detail="Slide deck / carousel",
        documentation="A deck of slides shown one at a time. Keys: slides (required list), label, auto_advance, delay, loop, folder (zCLI page-slides).",
        insert_text="zSwiper:\n    slides:\n        - ",
        priority=1
    ),
    UIElement(
        label="zDash",
        detail="Assembled dashboard",
        documentation="Compose a folder of pages into a sidebar shell. Keys: type (sidebar), folder, sidebar [Panel, ...], default.",
        insert_text="zDash:\n    type:    sidebar\n    folder:  \n    sidebar: []\n    default: ",
        priority=1
    ),
    UIElement(
        label="zProgress",
        detail="Progress bar / spinner",
        documentation="A labelled progress bar. Keys: label, current (default 0), total (omit for spinner), color, type (bar/spinner). Percentage is derived.",
        insert_text="zProgress:\n    label:   \n    current: 0\n    total:   100",
        priority=1
    ),

    # Dispatch display events
    UIElement(
        label="zMenu",
        detail="Interactive menu",
        documentation=(
            "Interactive menu gate. Options render as buttons; clicking an option "
            "sequentially reveals its content and all subsequent options (wizard-flow).\n\n"
            "Properties:\n"
            "  options: [list of option keys]  (required)\n"
            "  title: string                   (optional)\n"
            "  zAnchor: bool                   (~ shorthand — suppresses Back button, default false)\n\n"
            "Each option key maps to a nested display block.\n\n"
            "Shorthand: `*` suffix → zMenu; `~*` → zMenu with zAnchor: true"
        ),
        insert_text="zMenu:\n    title: \n    options: []\n    ",
        priority=1
    ),

    # Import event
    UIElement(
        label="zImport",
        detail="Import data from file into a model",
        documentation=(
            "Import event — reads a source file and inserts rows into a target model.\n\n"
            "Properties:\n"
            "  format:  csv | json | tsv  (required)\n"
            "  source:  zPath dot-notation to source file (required)\n"
            "  target:  zPath dot-notation to model (required)\n"
            "  mode:    append | replace  (default: append)\n\n"
            "Source path examples:\n"
            "  @.Data.imports.contacts.csv\n"
            "  @.Data.imports.zConv.filename  (after zDialog)\n\n"
            "Example:\n"
            "  zImport:\n"
            "      format: csv\n"
            "      source: @.Data.imports.contacts.csv\n"
            "      target: @.models.zSchema.crm.contacts\n"
            "      mode:   append"
        ),
        insert_text=(
            "zImport:\n"
            "    format: csv\n"
            "    source: @.Data.imports.\n"
            "    target: @.models.zSchema.\n"
            "    mode:   append"
        ),
        priority=1
    ),

    # Export event
    UIElement(
        label="zExport",
        detail="Export data to file or download",
        documentation=(
            "Export event — sources data and delivers it as a file.\n\n"
            "Properties:\n"
            "  format:   csv | json | tsv | txt  (required)\n"
            "  filename: string — output name, no extension (optional, default: 'export')\n"
            "  zData:    owned sub-block — silent read, rows piped to encoder\n"
            "  content:  raw value to export (alternative to zData)\n\n"
            "Delivery:\n"
            "  zCLI    → writes Data/exports/{filename}.{format}, prints path\n"
            "  Bifrost → pushes download event over WebSocket\n\n"
            "Example:\n"
            "  zExport:\n"
            "      format:   csv\n"
            "      filename: contacts_export\n"
            "      zData:\n"
            "          action: read\n"
            "          model:  @.models.zSchema.crm.contacts"
        ),
        insert_text="zExport:\n    format:   csv\n    filename: \n    zData:\n        action: read\n        model:  ",
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
