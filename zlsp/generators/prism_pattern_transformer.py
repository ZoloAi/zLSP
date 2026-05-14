"""
Prism Pattern Transformer

Transforms zlsp patterns to Prism-compatible regex patterns.
Handles differences between line-by-line parsing and multiline regex matching.

IMPORTANT: Value patterns are now auto-generated from SSOT (value_pattern_generator.py)
to ensure Prism highlighting matches parser behavior exactly.
"""

import re
from typing import Dict, Any, List
from .value_pattern_generator import get_value_pattern_priority_map


def transform_comment_pattern() -> Dict[str, Any]:
    r"""
    Transform comment pattern from zlsp to Prism.
    
    SSOT: comment_processors.py
    - Full-line comments: # at line start (after optional whitespace)
    - Inline comments: #> ... <# (paired delimiters)
    - Standalone # in values (like #python, #section) is NOT a comment
    
    Pattern: Match either full-line or inline comments
    """
    return {
        'name': 'comment',
        'pattern': r'/(^[ \t]*#(?!>).*|#>[\s\S]*?<#)/m',
        'alias': 'comment',
        'greedy': True,
        'comment': 'Full-line comments (# at line start) and inline comments (#> ... <#)'
    }


def transform_type_hint_pattern() -> Dict[str, Any]:
    r"""
    Transform type hint pattern from zlsp to Prism.
    
    SSOT: value_emitters.py:352-362 emits THREE tokens:
    - TokenType.TYPE_HINT_PAREN for `(` (line 354)
    - TokenType.TYPE_HINT for `int`/`bool`/etc. (line 358)
    - TokenType.TYPE_HINT_PAREN for `)` (line 362)
    
    Pattern must match ONLY type hints after keys, NOT parentheses in values.
    Examples:
    - "port(int):" → match (type hint before colon)
    - "code: hello()" → DON'T match (parentheses in value)
    
    Prism: Use `inside` to tokenize content within parentheses
    """
    return {
        'name': 'type-hint',
        'pattern': r'/\([^)]+\)(?=\s*:)/',
        'inside': {
            'type-hint-paren': {
                'pattern': r'/[()]/','alias': 'punctuation',
                'comment': 'SSOT: TokenType.TYPE_HINT_PAREN (lavender/purple)'
            },
            'type-hint-text': {
                'pattern': r'/[^()]+/',
                'alias': 'type',
                'comment': 'SSOT: TokenType.TYPE_HINT (cyan)'
            }
        },
        'comment': 'SSOT: Type hints split into parens + text (only before colon)'
    }


def transform_modifier_pattern() -> Dict[str, Any]:
    r"""
    Transform modifier pattern from zlsp to Prism.
    
    zlsp: [*!^~](?=:)
    Prism: /[*!^~](?=:)/
    
    Why: Modifiers change key behavior (required*, computed^, etc.)
    """
    return {
        'name': 'modifier',
        'pattern': r'/[*!^~](?=:)/',
        'alias': 'operator',
        'comment': 'Key modifiers: * (required), ! (locked), ^ (computed), ~ (internal)'
    }


def transform_punctuation_pattern() -> List[Dict[str, Any]]:
    r"""
    Transform punctuation patterns from zlsp to Prism.
    
    SSOT: Brackets/braces are handled at value level (array/object patterns).
    Only colon punctuation is standalone.

    Returns:
        List of pattern dictionaries
    """
    return [
        {
            'name': 'colon',
            'pattern': r'/:/',
            'alias': 'punctuation',
            'comment': 'Colon separator (key-value)'
        }
    ]


def transform_number_pattern() -> Dict[str, Any]:
    r"""
    Transform number pattern from zlsp to Prism.

    Matches:
    - Integers: 42, 0, 1000
    - Floats: 3.14, 99.99
    - Scientific: 1.23e-4, 1e10
    - Negative: -42, -3.14

    Pattern: lookbehind for colon, then number (prevents matching digits in strings)
    """
    return {
        'name': 'number',
        'pattern': r'/(?<=:\s+)-?\d+\.?\d*(?:[eE][+-]?\d+)?(?=\s*$)/m',
        'alias': 'number',
        'lookbehind': True,
        'comment': 'Numeric literals after colon (int, float, scientific, negative)'
    }


def transform_boolean_pattern() -> Dict[str, Any]:
    r"""
    Transform boolean pattern from zlsp to Prism.

    Must match ONLY standalone true/false after colon, not as part of larger strings.
    Examples:
    - "enabled: true" → match (entire value is true)
    - "status: false alarm" → DON'T match (has more text after)
    
    Pattern: Match true/false only when it's the complete value (nothing after except end-of-line)
    """
    return {
        'name': 'boolean',
        'pattern': r'/(?<=:\s+)(?:true|false)(?=\s*$)/m',
        'alias': 'boolean',
        'lookbehind': True,
        'comment': 'Boolean literals (complete value, nothing after)'
    }


def transform_null_pattern() -> Dict[str, Any]:
    r"""
    Transform null pattern from zlsp to Prism.

    Must match ONLY standalone null after colon, not as part of larger strings.
    Examples:
    - "optional_value: null" → match (entire value is null)
    - "null_message: null value" → DON'T match (has more text after)
    
    Pattern: Match null only when it's the complete value (nothing after except end-of-line)
    """
    return {
        'name': 'null',
        'pattern': r'/(?<=:\s+)null(?=\s*$)/m',
        'alias': 'null',
        'lookbehind': True,
        'comment': 'Null literals (complete value, nothing after)'
    }


def transform_string_pattern() -> List[Dict[str, Any]]:
    r"""
    Transform string pattern from zlsp to Prism.
    
    SSOT: value_emitters.py:122-184
    - Arrays: value.startswith('[') and value.endswith(']')
    - Objects: value.startswith('{') and value.endswith('}')
    - Everything else: string (default)
    
    Returns list of patterns:
    1. Quoted strings (high priority)
    2. Arrays (structural brackets)
    3. Objects (structural braces)
    4. Unquoted strings (catch-all, lowest priority)
    """
    return [
        {
            'name': 'string-quoted',
            'pattern': r'/(["' + r"'])(?:\\.|(?!\1)[^\\\r\n])*\1/",
            'alias': 'string',
            'greedy': True,
            'comment': 'SSOT: Quoted string literals'
        },
        {
            'name': 'array',
            'pattern': r'/(?<=:\s*)\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]/',
            'alias': 'language-zolo',
            'lookbehind': True,
            'inside': {
                'bracket': {
                    'pattern': r'/[\[\]]/',
                    'alias': 'bracket'
                },
                'comma': {
                    'pattern': r'/,/',
                    'alias': 'punctuation'
                },
                'rest': 'Prism.languages.zolo'
            },
            'comment': 'SSOT: Arrays start with [ and end with ] (value_emitters.py:122-124)'
        },
        {
            'name': 'object',
            'pattern': r'/(?<=:\s*)\{[^{}]*:[^{}]*(?:\{[^{}]*\}[^{}]*)*\}/',
            'alias': 'language-zolo',
            'lookbehind': True,
            'inside': {
                'brace': {
                    'pattern': r'/[{}]/',
                    'alias': 'brace'
                },
                'comma': {
                    'pattern': r'/,/',
                    'alias': 'punctuation'
                },
                'property': {
                    'pattern': r'/[a-zA-Z][a-zA-Z0-9_]*(?=\s*(?:\([^)]+\))?\s*:)/',
                    'alias': 'property'
                },
                'colon': {
                    'pattern': r'/:/',
                    'alias': 'punctuation'
                },
                'rest': 'Prism.languages.zolo'
            },
            'comment': 'SSOT: Objects start with { and end with } (value_emitters.py:127-129)'
        },
        {
            'name': 'string-unquoted',
            'pattern': r'/\S+(?:\s+\S+)*/',
            'alias': 'string',
            'comment': 'SSOT: Default string (value_emitters.py:174-184) - string-first philosophy'
        }
    ]


def optimize_pattern_order(patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Optimize pattern order for Prism.js performance and correctness.
    
    Prism processes patterns in order, so more specific patterns must come first.
    
    Order rules:
    1. Comments (highest priority - can appear anywhere)
    2. Specific root keys (zSpark, zMeta, etc.) before generic root-key
    3. Specific nested keys before generic property
    4. Type hints and modifiers
    5. Value patterns (FROM SSOT - value_pattern_generator.py)
    6. Punctuation (lowest priority)
    
    CRITICAL: Value pattern priorities now come from SSOT to ensure
    arrays/objects are checked BEFORE strings (structural-first).
    
    Args:
        patterns: List of pattern dictionaries
        
    Returns:
        Reordered list of patterns for optimal matching
    """
    # Get value pattern priorities from SSOT
    value_priorities = get_value_pattern_priority_map()
    
    # Merge with key/structural priorities
    priority_order = {
        'comment': 0,
        # NOTE: str-type-hint patterns removed (incompatible with multiline in Prism.js)
        # Specific roots
        'zspark-root': 10,
        'zui-special-root': 10,
        'zschema-zmeta-root': 10,
        'zconfig-special-root': 10,
        'zenv-config-root': 10,
        'zenv-z-uppercase-root': 11,
        # Generic roots
        'root-key': 20,
        # Specific nested keys
        'zspark-nested': 30,
        'zmachine-locked-section': 30,
        'zmachine-editable-section': 30,
        'zconfig-property': 31,
        'zschema-zos-data': 30,
        'zschema-property': 31,
        'zrbac-key': 30,
        'control-flow-key': 30,
        'zui-element': 31,
        'zui-element-property': 32,
        'zsub-key': 30,
        'znavbar-nested': 30,
        'metadata': 31,
        # Generic nested
        'property': 40,
        # Modifiers and type hints
        'type-hint': 50,
        'modifier': 51,
        # Value patterns (FROM SSOT - auto-generated)
        **value_priorities,
        # Punctuation (after strings)
        'colon': 90,
        # Punctuation (lowest)
        'punctuation': 100,
    }
    
    def get_priority(pattern: Dict[str, Any]) -> int:
        name = pattern.get('name', '')
        return priority_order.get(name, 50)  # Default to middle priority
    
    return sorted(patterns, key=get_priority)


def validate_pattern(pattern: Dict[str, Any]) -> bool:
    """
    Validate a Prism pattern dictionary.
    
    Args:
        pattern: Pattern dictionary to validate
        
    Returns:
        True if pattern is valid
        
    Raises:
        ValueError: If pattern is invalid
    """
    required_fields = ['name', 'pattern']
    for field in required_fields:
        if field not in pattern:
            raise ValueError(f"Pattern missing required field: {field}")
    
    # Validate pattern is a regex string
    pattern_str = pattern['pattern']
    if not isinstance(pattern_str, str):
        raise ValueError(f"Pattern must be a string: {pattern}")
    
    # Basic regex validation (check it starts/ends with /)
    if not (pattern_str.startswith('/') and pattern_str.count('/') >= 2):
        raise ValueError(f"Pattern must be in /regex/ or /regex/flags format: {pattern_str}")
    
    return True


def extract_test_cases(pattern: Dict[str, Any]) -> List[tuple[str, bool]]:
    """
    Extract test cases from pattern comment if present.
    
    Test cases are embedded in comments like:
        comment: 'Description\n        Test: zSpark: → matches\n        Test: zspark: → no match'
    
    Args:
        pattern: Pattern dictionary
        
    Returns:
        List of (test_input, should_match) tuples
    """
    test_cases = []
    comment = pattern.get('comment', '')
    
    for line in comment.split('\n'):
        line = line.strip()
        if line.startswith('Test:'):
            # Format: "Test: input → matches/no match"
            parts = line[5:].split('→')
            if len(parts) == 2:
                test_input = parts[0].strip()
                should_match = 'match' in parts[1].lower() and 'no' not in parts[1].lower()
                test_cases.append((test_input, should_match))
    
    return test_cases
