"""
Token Type Definitions

Defines the TokenType enum for semantic token classification.
This is the single source of truth for all token types in the LSP.
"""

from enum import Enum


class TokenType(Enum):
    """Semantic token types for .zolo syntax elements."""
    # Basic token types
    COMMENT = "comment"
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    NULL = "null"
    TYPE_HINT = "typeHint"
    TYPE_HINT_PAREN = "typeHintParen"
    COLON = "colon"
    COMMA = "comma"
    BRACKET_STRUCTURAL = "bracketStructural"
    BRACE_STRUCTURAL = "braceStructural"
    STRING_BRACKET = "stringBracket"  # [ ] inside string values
    STRING_BRACE = "stringBrace"      # { } inside string values
    ESCAPE_SEQUENCE = "escapeSequence"
    VERSION_STRING = "versionString"
    TIMESTAMP_STRING = "timestampString"
    TIME_STRING = "timeString"
    RATIO_STRING = "ratioString"
    ROOT_KEY = "rootKey"
    NESTED_KEY = "nestedKey"

    # Zolo-specific token types
    ZMETA_KEY = "zmetaKey"  # Special key for zMeta in zUI files
    ZOS_DATA_KEY = "zosDataKey"  # zOS zData keys under zMeta in zSchema.*.zolo files (purple 98)
    ZSCHEMA_PROPERTY_KEY = "zschemaPropertyKey"  # Field property keys in zSchema files (type, pk, etc.) - purple 98
    BIFROST_KEY = "bifrostKey"  # Underscore-prefixed keys: _zClass, etc.
    UI_ELEMENT_KEY = "uiElementKey"  # z-prefixed UI keys: zImage, zNavBar, zUL, zSub, etc.
    CONTROL_FLOW_KEY = "controlFlowKey"  # Control flow construct keys: zWizard (sequential UI flows) - light green
    UI_ELEMENT_PROPERTY_KEY = "uiElementPropertyKey"  # Property keys inside UI elements (src, label, color) - lavender
    ZCONFIG_KEY = "zconfigKey"  # z-prefixed root keys in zConfig.*.zolo files (e.g., zMachine) - light green
    ZSPARK_KEY = "zsparkKey"  # zSpark root key in zSpark.*.zolo files (light green)
    ZENV_CONFIG_KEY = "zenvConfigKey"  # Config root keys in zEnv.*.zolo (DEPLOYMENT, DEBUG, LOG_LEVEL) - purple 98
    ZNAVBAR_NESTED_KEY = "znavbarNestedKey"  # First-level nested keys under ZNAVBAR in zEnv - ANSI 222
    ZSUB_KEY = "zsubKey"  # zSub key in zEnv/zUI files at grandchild+ level (indent >= 4) - purple 98
    ZSPARK_NESTED_KEY = "zsparkNestedKey"  # ALL nested keys under zSpark root in zSpark files (purple 98)
    ZCONFIG_NESTED_KEY = "zconfigNestedKey"  # ALL nested keys under zMachine root in zConfig files (lavender)
    ZSPARK_MODE_VALUE = "zsparkModeValue"  # zMode value (zCLI/zBifrost) - tomato red 196
    ZSPARK_VAFILE_VALUE = "zsparkVaFileValue"  # zVaFile value (zUI.*) - dark green 40
    ZSPARK_SPECIAL_VALUE = "zsparkSpecialValue"  # zBlock value - light purple 99
    ENV_CONFIG_VALUE = "envConfigValue"  # Environment/config constants (PROD, DEBUG, INFO, etc.) - bright yellow 226
    ZRBAC_KEY = "zrbacKey"  # zRBAC access control key in zEnv/zUI files (tomato red 196)
    ZRBAC_OPTION_KEY = "zrbacOptionKey"  # zRBAC nested option keys: zGuest, authenticated, require_role, etc. (purple)
    ZMACHINE_EDITABLE_KEY = "zmachineEditableKey"  # Editable zMachine section keys (blue/cyan - INFO)
    ZMACHINE_LOCKED_KEY = "zmachineLockedKey"  # Auto-detected zMachine section keys (red/orange - ERROR)
    ZPATH_VALUE = "zpathValue"  # zPath data references: @.static.brand.logo.png, ~.config.settings (cyan)
    DISPATCH_KEY = "dispatchKey"  # zDispatch event keys: zDialog, zData, zCRUD, zLogin (golden)
