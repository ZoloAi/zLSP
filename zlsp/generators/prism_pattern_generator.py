"""
Prism Pattern Generator

Generates Prism.js patterns from zlsp SSOT for all file types.
Orchestrates file_type_pattern_extractor and prism_pattern_transformer.

IMPORTANT: Value patterns are now auto-generated from SSOT (value_pattern_generator.py)
to ensure Prism highlighting matches parser behavior exactly.
"""

from typing import List, Dict, Any
from zlsp.parser.zvaf.file_type_detector import FileType
from .file_type_pattern_extractor import (
    extract_root_key_patterns,
    extract_nested_key_patterns,
    extract_modifier_patterns,
    extract_value_patterns,
    get_file_type_config,
    get_all_file_types,
)
from .prism_pattern_transformer import (
    transform_comment_pattern,
    transform_type_hint_pattern,
    transform_modifier_pattern,
    transform_punctuation_pattern,
    optimize_pattern_order,
    validate_pattern,
)
from .value_pattern_generator import generate_value_patterns_from_ssot


def generate_base_patterns() -> List[Dict[str, Any]]:
    """
    Generate universal base patterns for zolo language.
    
    These patterns apply to ALL .zolo files and form the foundation
    for specialized languages (zspark, zui, etc.).
    
    Includes:
    - Comments
    - Root/nested keys
    - Type hints
    - Value patterns (AUTO-GENERATED FROM SSOT)
    - Punctuation
    
    Returns:
        List of pattern dictionaries for base zolo language
    """
    patterns = []
    
    # 1. Comments (highest priority)
    patterns.append(transform_comment_pattern())
    
    # 2. Type hint (str) override - CRITICAL: Must come before root-key/property patterns
    # SSOT: value_emitters.py:emit_value_tokens() lines 94-104
    # When type_hint == 'str', parser emits STRING token regardless of value content
    # These patterns match entire lines with (str) type hints to claim them before other patterns
    
    # NOTE: (str) type hint patterns removed - Prism.js is line-based and can't handle
    # multiline strings properly. These patterns caused incorrect tokenization of
    # continuation lines. For accurate highlighting, use LSP semantic tokens in IDE.
    
    # 3. Root keys at column 0 (ANY case: app_name, Server, DEBUG_MODE)
    # Pattern: match at line start, no indentation
    patterns.append({
        'name': 'root-key',
        'pattern': r'/(^|\n)([a-zA-Z][a-zA-Z0-9_]*)(?=\s*(?:\([^)]+\))?[*!^~]?:)/m',
        'alias': 'class-name',
        'lookbehind': True,
        'comment': 'Root keys at column 0, any case (salmon)'
    })
    
    # 4. Nested keys (indented, any case)
    # Pattern: must have whitespace after newline
    patterns.append({
        'name': 'property',
        'pattern': r'/(?<=\n)[ \t]+[a-zA-Z][a-zA-Z0-9_]*(?=\s*(?:\([^)]+\))?[*!]?:)/m',
        'lookbehind': True,
        'comment': 'Nested keys with indentation (golden yellow)'
    })
    
    # 5. Type hints on property keys (e.g., port(int):, ssl(bool):)
    # SSOT: value_emitters.py:emit_type_hint_tokens() lines 94-112
    patterns.append(transform_type_hint_pattern())
    
    # 6. VALUE PATTERNS FROM SSOT (AUTO-GENERATED)
    # This ensures Prism matches parser behavior exactly:
    # - Arrays/objects BEFORE unquoted strings (structural-first)
    # - Primitives (bool/number/null) in correct order
    # - Specialized strings (timestamps, versions) before generic strings
    # - Generic strings LAST (catch-all)
    value_patterns = generate_value_patterns_from_ssot()
    patterns.extend(value_patterns)
    
    # 7. Punctuation (lowest priority)
    patterns.extend(transform_punctuation_pattern())
    
    # Validate all patterns
    for pattern in patterns:
        validate_pattern(pattern)
    
    # Optimize pattern order (uses SSOT priorities)
    patterns = optimize_pattern_order(patterns)
    
    return patterns


def generate_override_patterns_for_file_type(file_type: FileType) -> List[Dict[str, Any]]:
    """
    Generate file-type-specific override patterns.
    
    These patterns add to or override the base zolo patterns for
    specialized file types (zspark, zui, zenv, etc.).
    
    IMPORTANT: We must nullify/remove the generic 'property' pattern
    from base, otherwise it will match before file-specific patterns.
    
    Args:
        file_type: The file type to generate overrides for
        
    Returns:
        List of pattern dictionaries to add/override in extended language
    """
    patterns = []
    
    # 1. File-type-specific root keys (override base root-key)
    patterns.extend(extract_root_key_patterns(file_type))
    
    # 2. File-type-specific nested keys
    nested_key_patterns = extract_nested_key_patterns(file_type)
    patterns.extend(nested_key_patterns)
    
    # 3. CRITICAL: Disable base 'property' only when nested patterns don't include their own.
    # If extract_nested_key_patterns already provides a 'property' override, adding null
    # here would kill it (duplicate key in JS object literal → last value wins).
    if nested_key_patterns:
        has_custom_property = any(
            p['name'] == 'property' and p.get('pattern') != 'null'
            for p in nested_key_patterns
        )
        if not has_custom_property:
            patterns.append({
                'name': 'property',
                'pattern': 'null',
                'comment': 'Disable generic property pattern - use file-specific patterns instead'
            })
    
    # 4. File-type-specific modifiers (zVaF files only)
    patterns.extend(extract_modifier_patterns(file_type))
    
    # 5. File-type-specific value patterns
    patterns.extend(extract_value_patterns(file_type))
    
    # Validate all patterns (except null overrides)
    for pattern in patterns:
        if pattern['pattern'] != 'null':
            validate_pattern(pattern)
    
    # Optimize pattern order
    patterns = optimize_pattern_order(patterns)
    
    return patterns


def generate_language_configs() -> Dict[FileType, Dict[str, Any]]:
    """
    Generate configuration for all language variants.
    
    Returns:
        Dict mapping FileType to language metadata (name, display name, description)
    """
    configs = {}
    for file_type in get_all_file_types():
        configs[file_type] = get_file_type_config(file_type)
    return configs


def build_prism_base_language(patterns: List[Dict[str, Any]]) -> str:
    """
    Build the base zolo language definition.
    
    This is the foundation that all specialized languages extend.
    Contains universal patterns: comments, strings, numbers, booleans, basic keys.
    
    Args:
        patterns: List of pattern dictionaries for base zolo
        
    Returns:
        JavaScript code defining Prism.languages.zolo
    """
    lines = [
        "/**",
        " * Prism.js base language definition for zolo",
        " * Generic .zolo syntax - string-first philosophy",
        " *",
        " * This is the foundation for all specialized zolo languages.",
        " * Other languages extend this base with file-type-specific patterns.",
        " *",
        " * Generated by zlsp/zlsp/generators/generate_prism_zolo.py",
        " * DO NOT EDIT MANUALLY - regenerate with: python3 -m zlsp.generators.generate_prism_zolo",
        " */",
        "",
        "Prism.languages.zolo = {",
    ]
    
    # Build pattern entries
    for i, pattern in enumerate(patterns):
        lines.extend(_build_pattern_entry(pattern, i == len(patterns) - 1))
    
    # Close language definition
    lines.append("};")
    lines.append("")
    
    return '\n'.join(lines)


def build_prism_extended_language(
    language_name: str,
    base_patterns: List[Dict[str, Any]],
    override_patterns: List[Dict[str, Any]],
    description: str
) -> str:
    """
    Build an extended Prism language that inherits from base zolo.
    
    If no overrides exist, creates a pure alias to base zolo.
    Otherwise, uses Prism.languages.extend() to add/override patterns.
    
    Args:
        language_name: Name of the language (e.g., 'zspark', 'zui')
        base_patterns: Base zolo patterns (for reference/ordering)
        override_patterns: File-type-specific patterns to add/override
        description: Language description for header comment
        
    Returns:
        JavaScript code defining the extended language
    """
    lines = [
        "/**",
        f" * Prism.js language definition for {language_name}",
        f" * {description}",
        " *",
    ]
    
    # If no overrides, create a pure alias
    if not override_patterns:
        lines.extend([
            " * Pure alias to base 'zolo' language (no custom patterns).",
            " *",
            " * Generated by zlsp/zlsp/generators/generate_prism_zolo.py",
            " * DO NOT EDIT MANUALLY - regenerate with: python3 -m zlsp.generators.generate_prism_zolo",
            " */",
            "",
            f"Prism.languages.{language_name} = Prism.languages.zolo;",
            ""
        ])
        
        # Add capitalized alias if language name is all lowercase (e.g., zspark → zSpark)
        if language_name.islower() and language_name.startswith('z'):
            # Short acronyms (len==3, e.g. zui→zUI): uppercase all chars after z
            # Longer names (e.g. zspark→zSpark): capitalize first char after z only
            suffix = language_name[1:]
            capitalized = language_name[0] + (suffix.upper() if len(suffix) <= 2 else suffix[0].upper() + suffix[1:])
            lines.extend([
                f"// Support both ```{language_name} and ```{capitalized} code fences",
                f"Prism.languages.{capitalized} = Prism.languages.{language_name};",
                ""
            ])
    else:
        lines.extend([
            " * Extends base 'zolo' language with file-type-specific patterns.",
            " *",
            " * Generated by zlsp/zlsp/generators/generate_prism_zolo.py",
            " * DO NOT EDIT MANUALLY - regenerate with: python3 -m zlsp.generators.generate_prism_zolo",
            " */",
            "",
            f"Prism.languages.{language_name} = Prism.languages.extend('zolo', {{",
        ])
        
        # Separate patterns into three groups:
        # 1. Value patterns → insertBefore('string-unquoted') for priority
        # 2. Key patterns with insert_before flag → insertBefore(target) for priority
        # 3. All other patterns → extend() block
        value_patterns = [p for p in override_patterns if p.get('name', '').endswith(('-value', '-context'))]
        insert_before_patterns = [p for p in override_patterns
                                   if p.get('insert_before') and not p.get('name', '').endswith(('-value', '-context'))]
        extend_patterns = [p for p in override_patterns
                           if not p.get('name', '').endswith(('-value', '-context'))
                           and not p.get('insert_before')]
        
        # Build extend block with non-special patterns only
        for i, pattern in enumerate(extend_patterns):
            lines.extend(_build_pattern_entry(pattern, i == len(extend_patterns) - 1))
        
        # Close language definition
        lines.append("});")
        lines.append("")
        
        # Group insert_before patterns by their target anchor
        if insert_before_patterns:
            from collections import defaultdict
            by_target = defaultdict(list)
            for p in insert_before_patterns:
                by_target[p['insert_before']].append(p)
            
            for target, patterns_group in by_target.items():
                lines.append(f"// Insert key patterns BEFORE '{target}' for correct priority")
                lines.append(f"Prism.languages.insertBefore('{language_name}', '{target}', {{")
                for i, pattern in enumerate(patterns_group):
                    is_last = (i == len(patterns_group) - 1)
                    for line in _build_pattern_entry(pattern, is_last):
                        lines.append(f"    {line}")
                lines.append("});")
            lines.append("")
        
        # Add value patterns via insertBefore for proper priority
        if value_patterns:
            lines.append("// Insert value patterns BEFORE string-unquoted for priority")
            for pattern in value_patterns:
                pattern_name = pattern['name']
                lines.append(f"Prism.languages.insertBefore('{language_name}', 'string-unquoted', {{")
                # Build pattern inline (without trailing comma since it's the only entry)
                for line in _build_pattern_entry(pattern, True):
                    lines.append(f"    {line}")
                lines.append("});")
            lines.append("")
        
        # Add capitalized alias if language name is all lowercase (e.g., zspark → zSpark)
        if language_name.islower() and language_name.startswith('z'):
            # Short acronyms (len==3, e.g. zui→zUI): uppercase all chars after z
            # Longer names (e.g. zspark→zSpark): capitalize first char after z only
            suffix = language_name[1:]
            capitalized = language_name[0] + (suffix.upper() if len(suffix) <= 2 else suffix[0].upper() + suffix[1:])
            lines.extend([
                f"// Support both ```{language_name} and ```{capitalized} code fences",
                f"Prism.languages.{capitalized} = Prism.languages.{language_name};",
                ""
            ])
    
    return '\n'.join(lines)


def _build_pattern_entry(pattern: Dict[str, Any], is_last: bool) -> List[str]:
    """
    Build a single pattern entry for Prism language definition.
    
    Handles both regular patterns and null overrides (to remove base patterns).
    
    Args:
        pattern: Pattern dictionary
        is_last: Whether this is the last pattern (affects comma)
        
    Returns:
        List of lines for this pattern entry
    """
    lines = []
    name = pattern['name']
    pattern_str = pattern['pattern']
    
    # Handle null pattern (to remove/disable inherited pattern)
    if pattern_str == 'null':
        if is_last:
            lines.append(f"    '{name}': null")
        else:
            lines.append(f"    '{name}': null,")
        return lines
    
    # Extract regex and flags
    # Pattern format: /regex/ or /regex/flags
    parts = pattern_str.split('/')
    if len(parts) >= 3:
        regex_body = '/'.join(parts[1:-1])  # Handle / inside regex
        flags = parts[-1] if parts[-1] else ''
    else:
        regex_body = pattern_str.strip('/')
        flags = ''
    
    # Build pattern object
    lines.append(f"    '{name}': {{")
    
    # Pattern with flags
    if flags:
        lines.append(f"        pattern: /{regex_body}/{flags},")
    else:
        lines.append(f"        pattern: /{regex_body}/,")
    
    # Alias (if present)
    if 'alias' in pattern:
        lines.append(f"        alias: '{pattern['alias']}',")
    
    # Lookbehind (if present)
    if pattern.get('lookbehind'):
        lines.append(f"        lookbehind: {str(pattern['lookbehind']).lower()},")
    
    # Greedy (if present)
    if pattern.get('greedy'):
        lines.append(f"        greedy: {str(pattern['greedy']).lower()},")
    
    # Inside (nested tokenization) - if present
    if 'inside' in pattern:
        inside_value = pattern['inside']
        
        # Handle direct string reference (e.g., 'Prism.languages.zolo')
        if isinstance(inside_value, str):
            lines.append(f"        inside: {inside_value},")
        # Handle dictionary of patterns
        else:
            lines.append("        inside: {")
            inside_patterns = inside_value
            inside_keys = list(inside_patterns.keys())
            for idx, key in enumerate(inside_keys):
                is_last_inside = (idx == len(inside_keys) - 1)
                inner = inside_patterns[key]
                
                # Handle special 'rest' reference
                if isinstance(inner, str):
                    if is_last_inside:
                        lines.append(f"            '{key}': {inner}")
                    else:
                        lines.append(f"            '{key}': {inner},")
                else:
                    lines.append(f"            '{key}': {{")
                    lines.append(f"                pattern: {inner['pattern']},")
                    if 'alias' in inner:
                        lines.append(f"                alias: '{inner['alias']}',")
                    if 'lookbehind' in inner:
                        lines.append(f"                lookbehind: {str(inner['lookbehind']).lower()},")
                    if 'greedy' in inner:
                        lines.append(f"                greedy: {str(inner['greedy']).lower()},")
                    # Handle nested inside (recursive)
                    if 'inside' in inner:
                        if isinstance(inner['inside'], str):
                            lines.append(f"                inside: {inner['inside']},")
                        else:
                            # Nested dictionary - recursively build it
                            lines.append("                inside: {")
                            nested_patterns = inner['inside']
                            nested_keys = list(nested_patterns.keys())
                            for nested_idx, nested_key in enumerate(nested_keys):
                                is_last_nested = (nested_idx == len(nested_keys) - 1)
                                nested_inner = nested_patterns[nested_key]
                                
                                if isinstance(nested_inner, str):
                                    if is_last_nested:
                                        lines.append(f"                    '{nested_key}': {nested_inner}")
                                    else:
                                        lines.append(f"                    '{nested_key}': {nested_inner},")
                                else:
                                    lines.append(f"                    '{nested_key}': {{")
                                    lines.append(f"                        pattern: {nested_inner['pattern']},")
                                    if 'alias' in nested_inner:
                                        lines.append(f"                        alias: '{nested_inner['alias']}',")
                                    if 'lookbehind' in nested_inner:
                                        lines.append(f"                        lookbehind: {str(nested_inner['lookbehind']).lower()},")
                                    if 'greedy' in nested_inner:
                                        lines.append(f"                        greedy: {str(nested_inner['greedy']).lower()},")
                                    # Handle third level of nesting (inside → inside → inside)
                                    if 'inside' in nested_inner:
                                        if isinstance(nested_inner['inside'], str):
                                            lines.append(f"                        inside: {nested_inner['inside']},")
                                        else:
                                            # Third level dictionary
                                            lines.append("                        inside: {")
                                            third_level_patterns = nested_inner['inside']
                                            third_level_keys = list(third_level_patterns.keys())
                                            for third_idx, third_key in enumerate(third_level_keys):
                                                is_last_third = (third_idx == len(third_level_keys) - 1)
                                                third_inner = third_level_patterns[third_key]
                                                
                                                if isinstance(third_inner, str):
                                                    if is_last_third:
                                                        lines.append(f"                            '{third_key}': {third_inner}")
                                                    else:
                                                        lines.append(f"                            '{third_key}': {third_inner},")
                                                else:
                                                    lines.append(f"                            '{third_key}': {{")
                                                    lines.append(f"                                pattern: {third_inner['pattern']},")
                                                    if 'alias' in third_inner:
                                                        lines.append(f"                                alias: '{third_inner['alias']}',")
                                                    if 'lookbehind' in third_inner:
                                                        lines.append(f"                                lookbehind: {str(third_inner['lookbehind']).lower()},")
                                                    if 'greedy' in third_inner:
                                                        lines.append(f"                                greedy: {str(third_inner['greedy']).lower()},")
                                                    if is_last_third:
                                                        lines.append("                            }")
                                                    else:
                                                        lines.append("                            },")
                                            lines.append("                        },")
                                    if is_last_nested:
                                        lines.append("                    }")
                                    else:
                                        lines.append("                    },")
                            lines.append("                },")

                    if is_last_inside:
                        lines.append("            }")
                    else:
                        lines.append("            },")
            lines.append("        },")
    
    # Close pattern object
    if is_last:
        lines.append("    }")
    else:
        lines.append("    },")
    
    return lines


def generate_test_cases_for_file_type(file_type: FileType) -> List[Dict[str, Any]]:
    """
    Generate test cases for a specific file type.
    
    Returns test inputs that should correctly highlight with the file-type-specific patterns.
    
    Args:
        file_type: The file type
        
    Returns:
        List of test case dictionaries with 'input', 'expected_tokens'
    """
    test_cases = []
    
    if file_type == FileType.ZSPARK:
        # DISABLED: zSpark being rebuilt from scratch
        # Now uses base zolo patterns (generic behavior)
        test_cases.append({
            'name': 'zSpark uses generic patterns',
            'input': 'zSpark:\n    title: MyApp',
            'expected': {
                'zSpark': 'root-key',      # Generic root key (not zspark-root)
                'title': 'property',       # Generic nested key (not zspark-nested)
                'MyApp': 'string-unquoted',
            }
        })
    
    elif file_type == FileType.ZUI:
        test_cases.append({
            'name': 'zUI special roots and elements',
            'input': 'zMeta:\n    zNavBar: true\nzVaF:\n    zH1:\n        label: Welcome',
            'expected': {
                'zMeta': 'zui-special-root',
                'zVaF': 'zui-special-root',
                'zH1': 'zui-element',
                'label': 'zui-element-property',
            }
        })
    
    elif file_type == FileType.ZSCHEMA:
        test_cases.append({
            'name': 'zSchema table and field properties',
            'input': 'zMeta:\n    Data_Type: SQL\nusers:\n    id:\n        type: int\n        pk: true',
            'expected': {
                'zMeta': 'zschema-zmeta-root',
                'Data_Type': 'zschema-zos-data',
                'users': 'root-key',
                'id': 'property',
                'type': 'zschema-property',
                'pk': 'zschema-property',
            }
        })
    
    elif file_type == FileType.ZCONFIG:
        test_cases.append({
            'name': 'zConfig sections',
            'input': 'zMachine:\n    machine_identity:\n        os: Darwin\n    user_preferences:\n        theme: dark',
            'expected': {
                'zMachine': 'zconfig-special-root',
                'machine_identity': 'zmachine-locked-section',
                'user_preferences': 'zmachine-editable-section',
                'os': 'zconfig-property',
                'theme': 'zconfig-property',
            }
        })
    
    elif file_type == FileType.ZENV:
        test_cases.append({
            'name': 'zEnv config and navbar',
            'input': 'DEPLOYMENT: Production\nZNAVBAR:\n    Home:\n        zPath: @.home\n    Docs:\n        zSub:\n            Guide: @.docs.guide',
            'expected': {
                'DEPLOYMENT': 'zenv-config-root',
                'ZNAVBAR': 'zenv-z-uppercase-root',
                'Home': 'znavbar-nested',
                'Docs': 'znavbar-nested',
                'zSub': 'zsub-key',
                '@.home': 'zpath-value',
                '@.docs.guide': 'zpath-value',
                'Production': 'env-constant-value',
            }
        })
    
    else:  # GENERIC
        test_cases.append({
            'name': 'Generic zolo syntax',
            'input': 'Settings_Page:\n    title: Settings\n    enabled: true',
            'expected': {
                'Settings_Page': 'root-key',
                'title': 'property',
                'enabled': 'property',
            }
        })
    
    return test_cases
