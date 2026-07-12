"""
File Type Pattern Extractor

Extracts file-type-specific token patterns from zlsp KeyDetector logic.
Maps KeyDetector.detect_root_key() and detect_nested_key() branches to Prism patterns.
"""

from typing import List, Dict, Any
from zlsp.parser.zvaf.file_type_detector import FileType
from zlsp.token_types import TokenType
from zlsp.token_registry import (
    ZOS_DATA_KEYS,
    ZSCHEMA_PROPERTY_KEYS,
    UI_ELEMENT_KEYS,
    UI_ELEMENT_PROPERTY_KEYS,
    DISPATCH_KEYS,
    CONTROL_FLOW_KEYS,
    ZENV_CONFIG_ROOT_KEYS,
    ZMACHINE_LOCKED_SECTIONS,
    ZMACHINE_EDITABLE_SECTIONS,
)


def extract_modifier_patterns(file_type: FileType) -> List[Dict[str, Any]]:
    """
    Extract modifier patterns for a file type.
    
    Modifiers are zVaF-specific (zUI, zEnv, zSpark only):
    - PREFIX: ^ (bounce), ~ (anchor) - appear BEFORE key name
    - SUFFIX: * (menu), ! (required) - appear AFTER key name, BEFORE colon
    
    SSOT: zlsp/parser/zvaf/modifier_handler.py lines 138-142
    In zEnv/zUI: prefix modifiers emit ZRBAC_OPTION_KEY (lavender #af87ff)
    """
    patterns = []
    
    # Modifiers only exist in zVaF files (zUI, zEnv)
    # DISABLED for zSpark: being rebuilt from scratch
    if file_type in [FileType.ZUI, FileType.ZENV]:
        # Prefix modifiers (^ or ~) before key name
        patterns.append({
            'name': 'prefix-modifier',
            'pattern': r'/[\^~](?=[a-zA-Z][a-zA-Z0-9_]*\s*:)/',
            'alias': 'variable',  # Maps to lavender
            'comment': 'Prefix modifiers (^logout:, ~anchor:) - lavender'
        })
        # Suffix modifiers (* or !) after key name, before colon
        patterns.append({
            'name': 'suffix-modifier',
            'pattern': r'/[*!](?=:)/',
            'alias': 'operator',  # Maps to yellow
            'comment': 'Suffix modifiers (menu*:, required!:) - yellow'
        })
    
    return patterns


def extract_root_key_patterns(file_type: FileType) -> List[Dict[str, Any]]:
    """
    Extract root key patterns for specific file type.
    
    Maps KeyDetector.detect_root_key() branches (lines 68-98) to Prism patterns.
    
    Args:
        file_type: The file type to generate patterns for
        
    Returns:
        List of Prism pattern dictionaries for root keys
    """
    patterns = []
    
    if file_type == FileType.ZSPARK:
        # DISABLED: zSpark being rebuilt from scratch
        # Use base zolo patterns (no overrides)
        # When ready to rebuild, add zSpark-specific patterns here
        pass
    
    elif file_type == FileType.ZUI:
        # Line 69-71: zMeta, zVaF are special in zUI files
        patterns.append({
            'name': 'zui-special-root',
            'pattern': r'/((?:^|\n)[ \t]*)(?:zMeta|zVaF)(?=\s*:)/m',
            'alias': 'function',
            'lookbehind': True,
            'comment': 'zUI special roots (green)'
        })
        # Generic roots (PascalCase or z-prefix like zHome)
        patterns.append({
            'name': 'root-key',
            'pattern': r'/(^|\n)([a-zA-Z][a-zA-Z0-9_]*)(?=\s*(?:\([^)]+\))?[*!^~]?:)/m',
            'alias': 'class-name',
            'lookbehind': True,
            'comment': 'Root keys at column 0 only (salmon)'
        })

    elif file_type == FileType.ZSCHEMA:
        # Line 70: zMeta is special in zSchema files
        patterns.append({
            'name': 'zschema-zmeta-root',
            'pattern': r'/((?:^|\n)[ \t]*)zMeta(?=\s*:)/m',
            'alias': 'function',
            'lookbehind': True,
            'comment': 'zMeta root in zSchema (green)'
        })
        # Table names (generic roots)
        patterns.append({
            'name': 'root-key',
            'pattern': r'/((?:^|\n)[ \t]*)[A-Z][a-zA-Z0-9_]*(?=\s*(?:\([^)]+\))?[*!^~]?:)/m',
            'alias': 'class-name',
            'lookbehind': True,
            'comment': 'Table names (pink/magenta)'
        })
    
    elif file_type == FileType.ZCONFIG:
        # Line 86-95: zMachine and Z-uppercase keys are special
        patterns.append({
            'name': 'zconfig-special-root',
            'pattern': r'/((?:^|\n)[ \t]*)(?:zMachine|Z[A-Z0-9_]+)(?=\s*:)/m',
            'alias': 'function',
            'lookbehind': True,
            'comment': 'zConfig special roots (green)'
        })
        # Generic roots
        patterns.append({
            'name': 'root-key',
            'pattern': r'/(^|\n)([A-Z][a-zA-Z0-9_]*)(?=\s*(?:\([^)]+\))?[*!^~]?:)/m',
            'alias': 'class-name',
            'lookbehind': True,
            'comment': 'Root keys at column 0 only (salmon)'
        })

    elif file_type == FileType.ZENV:
        # Line 78-79: Config root keys (DEPLOYMENT, DEBUG, LOG_LEVEL)
        config_keys = '|'.join(sorted(ZENV_CONFIG_ROOT_KEYS))
        patterns.append({
            'name': 'zenv-config-root',
            'pattern': rf'/((?:^|\n)[ \t]*)(?:{config_keys})(?=\s*:)/m',
            'alias': 'keyword',
            'lookbehind': True,
            'comment': 'zEnv config roots (purple)'
        })
        # Line 82-83: Z-uppercase keys (ZNAVBAR, ZSERVER_MOUNTS)
        patterns.append({
            'name': 'zenv-z-uppercase-root',
            'pattern': r'/((?:^|\n)[ \t]*)Z[A-Z0-9_]+(?=\s*:)/m',
            'alias': 'function',
            'lookbehind': True,
            'comment': 'Z-uppercase roots (green)'
        })
        # Generic uppercase roots
        patterns.append({
            'name': 'root-key',
            'pattern': r'/(^|\n)([A-Z][a-zA-Z0-9_]*)(?=\s*(?:\([^)]+\))?[*!^~]?:)/m',
            'alias': 'class-name',
            'lookbehind': True,
            'comment': 'Root keys at column 0 only (salmon)'
        })

    else:  # FileType.GENERIC
        # Generic root key pattern - column 0 only (NO indent)
        patterns.append({
            'name': 'root-key',
            'pattern': r'/(^|\n)([A-Z][a-zA-Z0-9_]*)(?=\s*(?:\([^)]+\))?[*!^~]?:)/m',
            'alias': 'class-name',
            'lookbehind': True,
            'comment': 'Root keys at column 0 only (salmon)'
        })
    
    return patterns


def extract_nested_key_patterns(file_type: FileType) -> List[Dict[str, Any]]:
    """
    Extract nested key patterns for specific file type.
    
    Maps KeyDetector.detect_nested_key() branches (lines 117-196) to Prism patterns.
    
    Args:
        file_type: The file type to generate patterns for
        
    Returns:
        List of Prism pattern dictionaries for nested keys
    """
    patterns = []
    
    if file_type == FileType.ZSPARK:
        # DISABLED: zSpark being rebuilt from scratch
        # Use base zolo nested key patterns (no overrides)
        pass
    
    elif file_type == FileType.ZCONFIG:
        # Line 127-128: Locked section headers (indent 1)
        locked_sections = '|'.join(sorted(ZMACHINE_LOCKED_SECTIONS))
        patterns.append({
            'name': 'zmachine-locked-section',
            'pattern': rf'/(?<=\n)[ \t]{{1}}(?:{locked_sections})(?=\s*:)/m',
            'alias': 'constant',
            'lookbehind': True,
            'comment': 'zMachine locked sections (red)'
        })
        # Line 129-130: Editable section headers (indent 1)
        editable_sections = '|'.join(sorted(ZMACHINE_EDITABLE_SECTIONS))
        patterns.append({
            'name': 'zmachine-editable-section',
            'pattern': rf'/(?<=\n)[ \t]{{1}}(?:{editable_sections})(?=\s*:)/m',
            'alias': 'variable',
            'lookbehind': True,
            'comment': 'zMachine editable sections (blue)'
        })
        # Line 135-136: Property keys (indent 2+)
        patterns.append({
            'name': 'zconfig-property',
            'pattern': r'/(?<=\n)[ \t]{2,}[a-zA-Z][a-zA-Z0-9_]*(?=\s*:)/m',
            'alias': 'variable',
            'lookbehind': True,
            'comment': 'zConfig properties (lavender)'
        })
    
    elif file_type == FileType.ZSCHEMA:
        # Line 153-155: zOS data keys under zMeta (indent 1)
        zos_data_keys = '|'.join(sorted(ZOS_DATA_KEYS))
        patterns.append({
            'name': 'zschema-zos-data',
            'pattern': rf'/(?<=\n)[ \t]{{1}}(?:{zos_data_keys})(?=\s*:)/m',
            'alias': 'keyword',
            'lookbehind': True,
            'comment': 'zOS data keys under zMeta (purple)'
        })
        # Line 160-161: Field properties (indent 2+)
        schema_props = '|'.join(sorted(ZSCHEMA_PROPERTY_KEYS))
        patterns.append({
            'name': 'zschema-property',
            'pattern': rf'/(?<=\n)[ \t]{{2,}}(?:{schema_props})(?=\s*:)/m',
            'alias': 'keyword',
            'lookbehind': True,
            'comment': 'Schema field properties (purple)'
        })
        # Generic nested keys (field names at indent 1)
        patterns.append({
            'name': 'property',
            'pattern': r'/\b[a-zA-Z][a-zA-Z0-9_]*(?=\s*(?:\([^)]+\))?[*!]?:)/',
            'comment': 'Field names (default)'
        })
    
    elif file_type == FileType.ZUI:
        # zGate — the one gate verb (auth / role / value / branch)
        patterns.append({
            'name': 'zgate-key',
            'pattern': r'/\bzGate(?=\s*:)/',
            'alias': 'constant',
            'insert_before': 'property',
            'comment': 'zGate access & conditional gate (red)'
        })
        # zRBAC key — DEPRECATED, folded into zGate; retained until leaves migrate
        patterns.append({
            'name': 'zrbac-key',
            'pattern': r'/\bzRBAC(?=\s*:)/',
            'alias': 'constant',
            'insert_before': 'property',
            'comment': 'zRBAC access control (red)'
        })
        # Line 175-176: Control flow + zLoom weaving keys (zWizard, zShuttle, zList, zKnot, zVar, zLoom)
        control_flow = '|'.join(sorted(CONTROL_FLOW_KEYS | {'zWizard'}))
        patterns.append({
            'name': 'control-flow-key',
            'pattern': rf'/\b(?:{control_flow})(?=\s*:)/',
            'alias': 'function',
            'insert_before': 'property',
            'comment': 'Control flow + zLoom constructs (green)'
        })
        # zDispatch event keys (zDialog, zData, zCRUD, zLogin) — golden
        dispatch_keys = '|'.join(sorted(DISPATCH_KEYS))
        patterns.append({
            'name': 'zdispatch-event',
            'pattern': rf'/\b(?:{dispatch_keys})(?=\s*(?:\([^)]+\))?[*!]?:)/',
            'alias': 'dispatch-event',
            'insert_before': 'property',
            'comment': 'zDispatch event keys (golden)'
        })
        # Line 180-186: UI element keys
        ui_elements = '|'.join(sorted(UI_ELEMENT_KEYS))
        patterns.append({
            'name': 'zui-element',
            'pattern': rf'/\b(?:{ui_elements})(?=\s*(?:\([^)]+\))?[*!]?:)/',
            'alias': 'function',
            'insert_before': 'property',
            'comment': 'UI elements (blue/yellow)'
        })
        # Line 189-193: UI element property keys
        ui_props = '|'.join(sorted(UI_ELEMENT_PROPERTY_KEYS))
        patterns.append({
            'name': 'zui-element-property',
            'pattern': rf'/\b(?:{ui_props})(?=\s*(?:\([^)]+\))?:)/',
            'alias': 'variable',
            'insert_before': 'property',
            'comment': 'UI element properties (lavender)'
        })
        # Line 164-167: zSub key
        patterns.append({
            'name': 'zsub-key',
            'pattern': r'/\bzSub(?=\s*:)/',
            'alias': 'keyword',
            'insert_before': 'property',
            'comment': 'Submenu key (purple)'
        })
        # Line 171-172: Bifrost metadata keys
        patterns.append({
            'name': 'metadata',
            'pattern': r'/\b_z[A-Z][a-zA-Z]+(?=:)/',
            'alias': 'keyword',
            'insert_before': 'property',
            'comment': 'Bifrost metadata (_zClass, _zStyle, etc.)'
        })
        # Generic nested keys
        patterns.append({
            'name': 'property',
            'pattern': r'/\b[a-zA-Z][a-zA-Z0-9_]*(?=\s*(?:\([^)]+\))?[*!]?:)/',
            'comment': 'Generic nested keys'
        })
    
    elif file_type == FileType.ZENV:
        # Line 149-150: ZNAVBAR first-level nested keys (indent 1)
        patterns.append({
            'name': 'znavbar-nested',
            'pattern': r'/(?<=\n)[ \t]{1}[a-zA-Z][a-zA-Z0-9_]*(?=\s*:)/m',
            'alias': 'type',
            'lookbehind': True,
            'comment': 'ZNAVBAR items (orange)'
        })
        # Line 164-166: zSub key (grandchild+, indent 2+)
        patterns.append({
            'name': 'zsub-key',
            'pattern': r'/(?<=\n)[ \t]{2,}zSub(?=\s*:)/m',
            'alias': 'keyword',
            'lookbehind': True,
            'comment': 'Submenu key (purple)'
        })
        # Line 139-140: zRBAC key
        patterns.append({
            'name': 'zrbac-key',
            'pattern': r'/\bzRBAC(?=\s*:)/',
            'alias': 'constant',
            'comment': 'zRBAC access control (red)'
        })
        # Generic nested keys (any case)
        patterns.append({
            'name': 'property',
            'pattern': r'/\b[a-zA-Z][a-zA-Z0-9_]*(?=\s*(?:\([^)]+\))?[*!]?:)/',
            'comment': 'Generic nested keys (any case)'
        })
    
    else:  # FileType.GENERIC
        # Generic nested key pattern (any case)
        patterns.append({
            'name': 'property',
            'pattern': r'/\b[a-zA-Z][a-zA-Z0-9_]*(?=\s*(?:\([^)]+\))?[*!]?:)/',
            'comment': 'Nested property keys (any case: label, content, Nested_zKey, etc.)'
        })
    
    return patterns


def extract_value_patterns(file_type: FileType) -> List[Dict[str, Any]]:
    """
    Extract value patterns for specific file type.
    
    Some file types have special value coloring (zPath, env constants, etc.).
    
    Args:
        file_type: The file type to generate patterns for
        
    Returns:
        List of Prism pattern dictionaries for values
    """
    patterns = []
    
    if file_type == FileType.ZENV:
        # zPath syntax: @.Data, ~.config
        patterns.append({
            'name': 'zpath-value',
            'pattern': r'/[@~]\.[a-zA-Z0-9_./]+/',
            'alias': 'string',
            'comment': 'zPath references (cyan)'
        })
        # Environment constants: DEBUG, PROD, INFO, WARNING, ERROR, etc.
        patterns.append({
            'name': 'env-constant-value',
            'pattern': r'/\b(?:DEBUG|PROD|INFO|WARNING|ERROR|CRITICAL|SESSION|Development|Production)\b/',
            'alias': 'number',
            'comment': 'Environment constants (yellow)'
        })
    
    elif file_type == FileType.ZSPARK:
        # Context-aware zPath highlighting: ONLY for zLogPath, zVaFolder, and zSpace keys
        # (zScrapath = deprecated alias of zLogPath, still highlighted)
        # Use lookbehind to match ONLY the zPath value after specific keys
        # This pattern will be inserted before string-unquoted to take priority
        # Matches: @ or ~ (bare root) OR @.path or ~.path (with components)
        patterns.append({
            'name': 'zspark-zpath-value',
            'pattern': r'/(?<=(?:zLogPath|zScrapath|zVaFolder|zSpace):\s*)[@~](?:\.[a-zA-Z0-9_./]+)?/',
            'alias': 'keyword',
            'lookbehind': True,
            'greedy': True,
            'comment': 'zPath values (cyan) - bare @ or ~ or with path - ONLY after specific keys'
        })

    elif file_type == FileType.ZUI:
        # Sigil-led values in zUI leaves. Names end in "-value" so the generator
        # inserts them BEFORE 'string-unquoted' (see build_prism_extended_language).
        # zPath references: @.zViews.file, ~.home.file (cyan)
        patterns.append({
            'name': 'zpath-value',
            'pattern': r'/[@~]\.[a-zA-Z0-9_./\- ]+/',
            'alias': 'string',
            'comment': 'zPath references (@. / ~.) — cyan',
        })
        # zFunc calls: &.plugin.fn(...), &.folder.file.fn, &zNow, &zUUID()
        patterns.append({
            'name': 'zfunc-value',
            'pattern': r'/&\.?[a-zA-Z][a-zA-Z0-9_.]*(?:\([^)]*\))?/',
            'alias': 'function',
            'comment': 'zFunc call sigil (&) — plugin/builtin calls',
        })
        # zLoom threads: %data.user.name, %session.x, %item.field, %var.x, %route.x
        patterns.append({
            'name': 'zloom-value',
            'pattern': r'/%[a-zA-Z][a-zA-Z0-9_.]*/',
            'alias': 'variable',
            'comment': 'zLoom % thread (spool/session/item/var/route)',
        })
        # zDelta same-file hop / $alias / $Block refs
        patterns.append({
            'name': 'zdelta-value',
            'pattern': r'/\$[a-zA-Z][a-zA-Z0-9_.]*/',
            'alias': 'variable',
            'comment': 'zDelta $Block / $alias reference',
        })

    return patterns


def get_file_type_config(file_type: FileType) -> Dict[str, Any]:
    """
    Get language configuration for a file type.
    
    Args:
        file_type: The file type
        
    Returns:
        Dictionary with language name, display name, and description
    """
    configs = {
        FileType.GENERIC: {
            'name': 'zolo',
            'displayName': 'Zolo (Generic)',
            'description': 'Generic .zolo syntax for REPL and generic files',
        },
        FileType.ZSPARK: {
            'name': 'zspark',
            'displayName': 'Zolo Spark',
            'description': 'zSpark.*.zolo - Application entry point configuration',
        },
        FileType.ZUI: {
            'name': 'zui',
            'displayName': 'Zolo UI',
            'description': 'zUI.*.zolo - User interface component files',
        },
        FileType.ZSCHEMA: {
            'name': 'zschema',
            'displayName': 'Zolo Schema',
            'description': 'zSchema.*.zolo - Data schema definition files',
        },
        FileType.ZCONFIG: {
            'name': 'zconfig',
            'displayName': 'Zolo Config',
            'description': 'zConfig.*.zolo - System configuration files',
        },
        FileType.ZENV: {
            'name': 'zenv',
            'displayName': 'Zolo Environment',
            'description': 'zEnv.*.zolo - Environment configuration files',
        },
    }
    return configs[file_type]


def get_all_file_types() -> List[FileType]:
    """
    Get list of all file types to generate languages for.
    
    Returns:
        List of FileType enum values
    """
    return [
        FileType.GENERIC,
        FileType.ZSPARK,
        FileType.ZUI,
        FileType.ZSCHEMA,
        FileType.ZCONFIG,
        FileType.ZENV,
    ]
