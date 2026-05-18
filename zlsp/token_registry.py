"""
Token Registry - Single Source of Truth for Token Type Mappings

This module centralizes all token type definitions, mappings, and key sets.
It auto-generates the LSP token type map and legend from a single source.

Key Design Principles:
1. Token types are defined once in token_types.py (TokenType enum)
2. This registry generates all mappings and legends automatically
3. Order matters for LSP - the TOKEN_TYPES_LEGEND order defines indices
4. Key sets for file-type detection are centralized here
"""

from typing import Dict, List, Set
from .token_types import TokenType


# =============================================================================
# LSP Token Type Registry
# =============================================================================
# CRITICAL: The order of this list defines the LSP token type indices!
# DO NOT REORDER without updating all clients (VS Code, Vim, etc.)
# =============================================================================

TOKEN_TYPES_LEGEND: List[str] = [
    "comment",              # 0  - MUST be first!
    "rootKey",              # 1
    "nestedKey",            # 2
    "zmetaKey",             # 3
    "zosDataKey",           # 4
    "zschemaPropertyKey",   # 5
    "bifrostKey",           # 6
    "controlFlowKey",       # 7
    "uiElementKey",         # 8
    "uiElementPropertyKey", # 9
    "zconfigKey",           # 10
    "zsparkKey",            # 11
    "zenvConfigKey",        # 12
    "znavbarNestedKey",     # 13
    "zsubKey",              # 14
    "zsparkNestedKey",      # 15
    "zconfigNestedKey",     # 16
    "zsparkModeValue",      # 17
    "zsparkVaFileValue",    # 18
    "zsparkSpecialValue",   # 19
    "envConfigValue",       # 20
    "zrbacKey",             # 21
    "zrbacOptionKey",       # 22
    "typeHint",             # 23
    "number",               # 24
    "string",               # 25
    "boolean",              # 26
    "null",                 # 27
    "bracketStructural",    # 28
    "braceStructural",      # 29
    "stringBracket",        # 30
    "stringBrace",          # 31
    "colon",                # 32
    "comma",                # 33
    "escapeSequence",       # 34
    "versionString",        # 35
    "timestampString",      # 36
    "timeString",           # 37
    "ratioString",          # 38
    "zpathValue",           # 39
    "zmachineEditableKey",  # 40
    "zmachineLockedKey",    # 41
    "typeHintParen",        # 42
    "dispatchKey",          # 43
]

TOKEN_MODIFIERS_LEGEND: List[str] = []  # No modifiers yet


# Auto-generate TOKEN_TYPE_MAP from TokenType enum and legend
# This ensures the enum values map to the correct indices
def _build_token_type_map() -> Dict[TokenType, int]:
    """
    Build the token type map from TokenType enum to LSP indices.
    
    This function maps each TokenType enum value to its index in TOKEN_TYPES_LEGEND.
    The mapping is based on the camelCase legend names matching the enum value strings.
    
    Returns:
        Dictionary mapping TokenType enum values to their LSP indices
    """
    token_map = {}

    for token_type in TokenType:
        # Convert enum value (camelCase) to match legend entries
        enum_value = token_type.value

        # Find the index in the legend
        try:
            index = TOKEN_TYPES_LEGEND.index(enum_value)
            token_map[token_type] = index
        except ValueError as exc:
            # Token type not in legend - this is a bug!
            raise ValueError(
                f"TokenType.{token_type.name} ('{enum_value}') not found in TOKEN_TYPES_LEGEND. "
                f"This is a bug - all token types must be in the legend."
            ) from exc

    return token_map


TOKEN_TYPE_MAP: Dict[TokenType, int] = _build_token_type_map()


# =============================================================================
# Block Type Constants
# =============================================================================
# Block type identifiers used by BlockTracker for nested block context tracking.
# These represent UI elements, config sections, and special blocks.
# =============================================================================

# UI element blocks (lowercase for internal tracking)
BLOCK_ZRBAC = 'zRBAC'
BLOCK_ZIMAGE = 'zimage'
BLOCK_ZTEXT = 'ztext'
BLOCK_ZMD = 'zmd'
BLOCK_ZCODE = 'zcode'
BLOCK_ZURL = 'zurl'
BLOCK_ZCRUMBS = 'zcrumbs'
BLOCK_HEADER = 'header'
BLOCK_ZUL = 'zul'
BLOCK_ZOL = 'zol'
BLOCK_ZDL = 'zdl'
BLOCK_ZTABLE = 'ztable'
BLOCK_ZINPUT = 'zinput'
BLOCK_ZLINK = 'zlink'
BLOCK_ZCHECKBOX = 'zcheckbox'
BLOCK_ZBTN = 'zbtn'
BLOCK_ZSELECT = 'zselect'
BLOCK_ZRANGE = 'zrange'

# Special blocks
BLOCK_ZMENU = 'zmenu'
BLOCK_PLURAL_SHORTHAND = 'plural_shorthand'
BLOCK_ZMACHINE = 'zMachine'
BLOCK_ZSPARK = 'zSpark'
BLOCK_ZNAVBAR = 'ZNAVBAR'
BLOCK_ZMETA = 'zMeta'

# Consolidated list of all UI element block types (for iteration/checking)
UI_ELEMENT_BLOCK_TYPES = [
    BLOCK_ZIMAGE, BLOCK_ZTEXT, BLOCK_ZMD, BLOCK_ZCODE, BLOCK_ZURL, BLOCK_ZUL, BLOCK_ZOL, BLOCK_ZDL,
    BLOCK_ZTABLE, BLOCK_HEADER, BLOCK_ZCRUMBS, BLOCK_ZINPUT, BLOCK_ZLINK,
    BLOCK_ZCHECKBOX, BLOCK_ZBTN, BLOCK_ZSELECT, BLOCK_ZRANGE, BLOCK_ZMENU
]


# =============================================================================
# Key Sets for File-Type Detection
# =============================================================================
# These sets define special keys used by the key detector for context-aware
# token type detection based on file type and nesting level.
# =============================================================================

# zOS zData keys under zMeta in zSchema files
ZOS_DATA_KEYS: Set[str] = {
    'Data_Type', 'Data_Label', 'Data_Source', 'Schema_Name', 
    'zMigration', 'zMigrationVersion'
}

# zSchema property keys (field properties)
ZSCHEMA_PROPERTY_KEYS: Set[str] = {
    'type', 'pk', 'auto_increment', 'unique', 'required', 
    'default', 'rules', 'format', 'min_length', 'max_length',
    'pattern', 'min', 'max', 'zHash', 'comment'
}

# UI element keys (z-prefixed UI components)
UI_ELEMENT_KEYS: Set[str] = {
    'zImage', 'zText', 'zMD', 'zCode', 'zURL', 'zNavBar', 'zUL', 'zOL', 'zDL', 'zTable',
    'zH0', 'zH1', 'zH2', 'zH3', 'zH4', 'zH5', 'zH6', 'zCrumbs', 'zInput', 'zLink',
    'zCheckbox', 'zBtn', 'zSelect', 'zRange', 'zFunc', 'zWizard', 'zTerminal',
    # Signal events
    'zSignal', 'zError', 'zWarning', 'zSuccess', 'zInfo',
}

# Plural shorthand keys (SSOT mirror for LSP — keep in sync with dispatch_constants.PLURAL_SHORTHAND_KEYS)
PLURAL_SHORTHAND_KEYS: Set[str] = {
    'zURLs', 'zTexts', 'zImages', 'zMDs',
    'zBtns', 'zInputs', 'zCheckboxes', 'zSelects', 'zRanges', 'zIcons',
    'zH0s', 'zH1s', 'zH2s', 'zH3s', 'zH4s', 'zH5s', 'zH6s',
}

# zDispatch event keys (z-prefixed dispatch commands that trigger backend actions)
DISPATCH_KEYS: Set[str] = {
    'zDialog', 'zData', 'zCRUD', 'zLogin', 'zDispatch', 'zMenu',
}

# Control flow construct keys (empty - zWizard moved to UI_ELEMENT_MAPPING for consistent coloring)
CONTROL_FLOW_KEYS: Set[str] = set()

# UI element property keys (properties inside UI elements)
UI_ELEMENT_PROPERTY_KEYS: Set[str] = {
    'src', 'alt_text', 'caption', 'color', 'open_prompt', 'indent',
    'label', 'style', 'semantic',
    'href', 'target', 'rel', 'window',
    'content', 'pause', 'break_message', 'format',
    'items',
    'title', 'columns', 'rows', 'limit', 'offset', 'show_header', 'interactive',
    'zAnchor',
    'show', 'parent',
    # Form-specific properties (zInput, zTextarea, zSelect, etc.)
    'prompt', 'type', 'placeholder', 'required', 'disabled', 'readonly',
    'min', 'max', 'step', 'pattern', 'autocomplete', 'value', 'checked',
    'name', 'id', 'maxlength', 'minlength', 'multiple', 'size', 'options', 'multi',
    'prefix', 'suffix',  # Input group properties
    # Button-specific properties (zBtn)
    'action'
}

# UI Element Schemas - Define valid properties per element type
UI_ELEMENT_SCHEMAS: Dict[str, Dict[str, List[str]]] = {
    'zimage': {
        'required': ['src'],
        'optional': ['alt_text', 'caption', '_zClass', '_id', 'color', 'open_prompt', 'indent'],
    },
    'header': {  # Covers zH1-zH6
        'required': [],
        'optional': ['label', 'color', 'style', 'indent', 'semantic', '_zClass', '_id'],
    },
    'zurl': {
        'required': ['label', 'href'],
        'optional': ['target', 'rel', 'window', 'color', '_zClass', '_id'],
    },
    'ztext': {
        'required': ['content'],
        'optional': ['indent', 'pause', 'break_message', 'semantic', 'color', '_zClass', '_id'],
    },
    'zmd': {
        'required': ['content'],
        'optional': ['indent', 'pause', 'break_message', 'format', 'color', '_zClass', '_id'],
    },
    'zul': {
        'required': ['items'],
        'optional': ['style', 'indent', '_zClass', '_id'],
    },
    'ztable': {
        'required': ['title', 'columns', 'rows'],
        'optional': ['limit', 'offset', 'show_header', 'interactive', 'indent', '_zClass', '_id', 'truncate'],
    },
    'zcrumbs': {
        'required': [],
        'optional': ['show', 'parent', '_zClass', '_id'],
    },
    'zinput': {
        'required': [],  # All properties are optional for flexibility
        'optional': [
            'prompt', 'type', 'placeholder', 'required', 'disabled', 'readonly',
            'min', 'max', 'step', 'pattern', 'autocomplete', 'value', 'checked',
            'name', 'id', 'maxlength', 'minlength', 'multiple', 'size',
            'prefix', 'suffix',  # Input group properties
            '_zClass', '_id', 'color', 'indent'
        ],
    },
    'zcheckbox': {
        'required': [],  # All properties are optional for flexibility
        'optional': [
            'prompt', 'checked', 'required', 'label', 'disabled',
            'name', 'id', 'value',
            '_zClass', '_id', 'color', 'indent'
        ],
    },
    'zbtn': {
        'required': [],  # All properties are optional for flexibility
        'optional': [
            'label', 'color', 'type', 'action', 'disabled',
            'name', 'id', 'value',
            '_zClass', '_id', 'indent'
        ],
    },
    # More elements to be added as needed
}

# Properties that are ALWAYS multiline (auto-enable without (str): hint)
# Maps UI element type to its multiline properties
AUTO_MULTILINE_PROPERTIES: Dict[str, Set[str]] = {
    'zmd': {'content'},           # Markdown content is always multiline
    'ztext': {'content'},         # Text content is always multiline
    'zcode': {'content'},         # Code content is always multiline
    'header': {'label'},          # Header labels can be multiline
    'zimage': {'caption'},        # Image captions can be multiline
    'zterminal': {'content'},     # Terminal code content is always multiline
    # Add more as needed
}

# =============================================================================
# UI Element Mappings (SSOT for UI element behavior)
# =============================================================================
# Maps UI element keys to their block types and properties.
# This is the SINGLE SOURCE OF TRUTH for UI element definitions.
# Adding a new UI element only requires updating this dictionary.
# =============================================================================

UI_ELEMENT_MAPPING: Dict[str, Dict[str, any]] = {
    'zImage': {
        'block_type': BLOCK_ZIMAGE,
        'block_name': 'zimage',
        'requires_zui': True,
        'is_shorthand': True,  # Can appear multiple times in sequence
    },
    'zText': {
        'block_type': BLOCK_ZTEXT,
        'block_name': 'ztext',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zMD': {
        'block_type': BLOCK_ZMD,
        'block_name': 'zmd',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zCode': {
        'block_type': BLOCK_ZCODE,
        'block_name': 'zcode',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zURL': {
        'block_type': BLOCK_ZURL,
        'block_name': 'zurl',
        'requires_zui': True,
        'is_shorthand': False,
    },
    'zUL': {
        'block_type': BLOCK_ZUL,
        'block_name': 'zul',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zTable': {
        'block_type': BLOCK_ZTABLE,
        'block_name': 'ztable',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zH1': {
        'block_type': BLOCK_HEADER,
        'block_name': 'header',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zH2': {
        'block_type': BLOCK_HEADER,
        'block_name': 'header',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zH3': {
        'block_type': BLOCK_HEADER,
        'block_name': 'header',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zH4': {
        'block_type': BLOCK_HEADER,
        'block_name': 'header',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zH5': {
        'block_type': BLOCK_HEADER,
        'block_name': 'header',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zH6': {
        'block_type': BLOCK_HEADER,
        'block_name': 'header',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zCrumbs': {
        'block_type': BLOCK_ZCRUMBS,
        'block_name': 'zcrumbs',
        'requires_zui': True,
        'is_shorthand': False,
    },
    'zInput': {
        'block_type': BLOCK_ZINPUT,
        'block_name': 'zinput',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zLink': {
        'block_type': BLOCK_ZLINK,
        'block_name': 'zlink',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zCheckbox': {
        'block_type': BLOCK_ZCHECKBOX,
        'block_name': 'zcheckbox',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zBtn': {
        'block_type': BLOCK_ZBTN,
        'block_name': 'zbtn',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zButton': {  # Alias for zBtn
        'block_type': BLOCK_ZBTN,
        'block_name': 'zbtn',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zSelect': {
        'block_type': BLOCK_ZSELECT,
        'block_name': 'zselect',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zRange': {
        'block_type': BLOCK_ZRANGE,
        'block_name': 'zrange',
        'requires_zui': True,
        'is_shorthand': False,
    },
    'zFunc': {
        'block_type': None,
        'block_name': None,
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zH0': {
        'block_type': BLOCK_HEADER,
        'block_name': 'header',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zWizard': {
        'block_type': None,
        'block_name': None,
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zTerminal': {  # Added for completeness
        'block_type': None,  # Define if needed
        'block_name': 'zterminal',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zMenu': {
        'block_type': BLOCK_ZMENU,
        'block_name': 'zmenu',
        'requires_zui': True,
        'is_shorthand': True,  # Can appear multiple times — __dup suffix for sequential menus
    },
    'zOL': {  # Ordered list
        'block_type': BLOCK_ZOL,
        'block_name': 'zol',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zDL': {  # Description list
        'block_type': BLOCK_ZDL,
        'block_name': 'zdl',
        'requires_zui': True,
        'is_shorthand': True,
    },
    # Signal events (zSignals family)
    'zSignal': {  # Longhand — type: error|warning|success|info, content: ...
        'block_type': None,
        'block_name': 'zsignal',
        'requires_zui': True,
        'is_shorthand': True,  # __dup allowed for multiple signals
    },
    'zError': {
        'block_type': None,
        'block_name': 'zerror',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zWarning': {
        'block_type': None,
        'block_name': 'zwarning',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zSuccess': {
        'block_type': None,
        'block_name': 'zsuccess',
        'requires_zui': True,
        'is_shorthand': True,
    },
    'zInfo': {
        'block_type': None,
        'block_name': 'zinfo',
        'requires_zui': True,
        'is_shorthand': True,
    },
}

# Derived sets for backward compatibility and quick lookups
UI_ELEMENT_SHORTHAND_KEYS: Set[str] = {
    key for key, props in UI_ELEMENT_MAPPING.items() 
    if props.get('is_shorthand', False)
}

# Special blocks mapping (non-UI elements that create block contexts)
SPECIAL_BLOCK_MAPPING: Dict[str, Dict[str, any]] = {
    'zRBAC': {
        'block_type': BLOCK_ZRBAC,
        'block_name': 'zrbac',
        'method': 'enter_block',  # Uses regular enter_block
    },
    'zMeta': {
        'block_type': BLOCK_ZMETA,
        'block_name': 'zmeta',
        'method': 'enter_block_single',  # Uses single-instance tracking
        'file_types': ['zschema'],  # Only in zSchema files
    },
    'ZNAVBAR': {
        'block_type': BLOCK_ZNAVBAR,
        'block_name': 'znavbar',
        'method': 'enter_block_single',
    },
    'zMachine': {
        'block_type': BLOCK_ZMACHINE,
        'block_name': 'zmachine',
        'method': 'enter_block',
    },
    'zSpark': {
        'block_type': BLOCK_ZSPARK,
        'block_name': 'zspark',
        'method': 'enter_block_single',
    },
}

# zEnv config root keys
ZENV_CONFIG_ROOT_KEYS: Set[str] = {'DEPLOYMENT', 'DEBUG', 'LOG_LEVEL'}

# zMachine section headers (first-level keys under zMachine:)
ZMACHINE_LOCKED_SECTIONS: Set[str] = {
    'machine_identity', 'python_runtime', 'cpu', 'memory', 'gpu', 
    'network', 'storage', 'user_paths', 'display', 'launch_commands',
}

ZMACHINE_EDITABLE_SECTIONS: Set[str] = {
    'user_preferences', 'time_date_formatting', 'custom',
}


# =============================================================================
# Validation Functions
# =============================================================================

def validate_token_registry() -> None:
    """
    Validate that the token registry is consistent.
    
    Checks:
    1. All TokenType enum values are in TOKEN_TYPES_LEGEND
    2. No duplicate indices in TOKEN_TYPE_MAP
    3. All legend entries have corresponding enum values
    
    Raises:
        ValueError: If validation fails
    """
    # Check 1: All enum values in legend
    for token_type in TokenType:
        if token_type.value not in TOKEN_TYPES_LEGEND:
            raise ValueError(
                f"TokenType.{token_type.name} ('{token_type.value}') not in TOKEN_TYPES_LEGEND"
            )

    # Check 2: No duplicate indices
    indices = list(TOKEN_TYPE_MAP.values())
    if len(indices) != len(set(indices)):
        raise ValueError("Duplicate indices found in TOKEN_TYPE_MAP")

    # Check 3: All legend entries have enum values
    enum_values = {t.value for t in TokenType}
    for legend_entry in TOKEN_TYPES_LEGEND:
        if legend_entry not in enum_values:
            raise ValueError(
                f"Legend entry '{legend_entry}' has no corresponding TokenType enum value"
            )


# Run validation on import to catch issues early
validate_token_registry()


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Token type mappings
    'TOKEN_TYPE_MAP',
    'TOKEN_TYPES_LEGEND',
    'TOKEN_MODIFIERS_LEGEND',

    # Block type constants
    'BLOCK_ZRBAC',
    'BLOCK_ZIMAGE',
    'BLOCK_ZTEXT',
    'BLOCK_ZMD',
    'BLOCK_ZURL',
    'BLOCK_ZCRUMBS',
    'BLOCK_HEADER',
    'BLOCK_ZUL',
    'BLOCK_ZTABLE',
    'BLOCK_ZINPUT',
    'BLOCK_ZLINK',
    'BLOCK_ZCHECKBOX',
    'BLOCK_ZBTN',
    'BLOCK_ZSELECT',
    'BLOCK_ZRANGE',
    'BLOCK_PLURAL_SHORTHAND',
    'BLOCK_ZMACHINE',
    'BLOCK_ZSPARK',
    'BLOCK_ZNAVBAR',
    'BLOCK_ZMETA',
    'UI_ELEMENT_BLOCK_TYPES',

    # Key sets for detection
    'ZOS_DATA_KEYS',
    'ZSCHEMA_PROPERTY_KEYS',
    'UI_ELEMENT_KEYS',
    'PLURAL_SHORTHAND_KEYS',
    'DISPATCH_KEYS',
    'CONTROL_FLOW_KEYS',
    'UI_ELEMENT_PROPERTY_KEYS',
    'UI_ELEMENT_SCHEMAS',
    'AUTO_MULTILINE_PROPERTIES',
    'UI_ELEMENT_MAPPING',
    'UI_ELEMENT_SHORTHAND_KEYS',
    'SPECIAL_BLOCK_MAPPING',
    'ZENV_CONFIG_ROOT_KEYS',
    'ZMACHINE_LOCKED_SECTIONS',
    'ZMACHINE_EDITABLE_SECTIONS',

    # Validation
    'validate_token_registry',
]
