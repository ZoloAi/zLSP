"""
Value Pattern Generator - Auto-generate Prism patterns from SSOT

This module extracts the exact value detection order from value_emitters.py
and generates Prism patterns that mirror the parser's by-value/string-first approach.

SSOT: zlsp/parser/core/value_emitters.py:emit_value_tokens() lines 18-185
"""

from typing import Dict, Any, List
from zlsp.token_types import TokenType


def generate_value_patterns_from_ssot() -> List[Dict[str, Any]]:
    """
    Auto-generate Prism value patterns by mirroring emit_value_tokens() logic.
    
    This ensures Prism highlighting matches parser behavior exactly.
    Order extracted from value_emitters.py:emit_value_tokens() lines 18-185.
    
    Detection Order (SSOT):
    1. Type hints (lines 94-112) - explicit override
    2. zPath values (lines 114-119) - context-specific
    3. Arrays (line 122) - structural BEFORE strings
    4. Objects (line 127) - structural BEFORE strings
    5. Booleans (line 132) - primitives
    6. Numbers (line 137) - primitives
    7. Null (line 142) - primitives
    8. Environment constants (line 149) - context-specific
    9. Specialized strings (lines 154-172) - timestamps, versions, ratios
    10. String (line 174) - DEFAULT fallback
    
    Returns:
        List of Prism pattern dictionaries in SSOT order
    """
    patterns = []
    
    # SSOT Line 122: Arrays BEFORE strings (structural-first)
    # SSOT: value_emitters.py:emit_array_tokens() uses depth counter for nesting (lines 260-264)
    # Pattern matches arrays with arbitrary nesting depth, including multiline arrays
    # MULTILINE SUPPORT: Matches across lines but requires array to be complete value
    # CRITICAL: (?=\s*(?:\n|$)) ensures array is followed by newline or end (not more text)
    # This prevents [1+2] in "math: [1+2] equals 3" from matching as array
    # NOTE: (str) type hint override handled by separate high-priority pattern in prism_pattern_generator.py
    patterns.append({
        'name': 'array',
        'pattern': r'/(?<=:\s*)\[(?:[^\[\]]|\[(?:[^\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\])*\])*\](?=\s*(?:\n|$))/ms',
        'alias': 'language-zolo',
        'lookbehind': True,
        'greedy': True,
        'inside': {
            'bracket': {
                'pattern': r'/[\[\]]/',
                'alias': 'bracket'
            },
            'comma': {
                'pattern': r'/,/',
                'alias': 'punctuation'
            },
            # CRITICAL: Inline objects MUST come BEFORE primitives to match {key: value1, nested: [a, b]}
            # Handles single-line inline objects within arrays
            'object': {
                'pattern': r'/\{(?:[^{}]|\{[^{}]*\})*\}/',
                'alias': 'language-zolo',
                'greedy': True,
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
                        'pattern': r'/[a-zA-Z][a-zA-Z0-9_]*(?=\s*:)/',
                        'alias': 'property'
                    },
                    'colon': {
                        'pattern': r'/:/',
                        'alias': 'punctuation'
                    },
                    # Nested arrays inside inline objects
                    'array': {
                        'pattern': r'/\[(?:[^\[\]]|\[(?:[^\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\])*\])*\]/',
                        'alias': 'language-zolo',
                        'greedy': True,
                        'inside': {
                            'bracket': {
                                'pattern': r'/[\[\]]/',
                                'alias': 'bracket'
                            },
                            'comma': {
                                'pattern': r'/,/',
                                'alias': 'punctuation'
                            },
                            'string': {
                                'pattern': r'/[^\[\],\s]+(?:\s+[^\[\],\s]+)*/',
                                'alias': 'string'
                            }
                        }
                    },
                    'boolean': {
                        'pattern': r'/\b(?:true|false|True|False)\b/',
                        'alias': 'boolean'
                    },
                    'null': {
                        'pattern': r'/\bnull\b/',
                        'alias': 'null'
                    },
                    'number': {
                        'pattern': r'/(?<![a-zA-Z0-9_])-?(?:0(?!\d)|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?(?![a-zA-Z0-9_])/',
                        'alias': 'number'
                    },
                    'string': {
                        'pattern': r'/[^{}\[\],:\s]+(?:\s+[^{}\[\],:\s]+)*/',
                        'alias': 'string'
                    }
                },
                'comment': 'Inline objects within arrays (e.g., {key: value, nested: [a, b]})'
            },
            # CRITICAL: Nested arrays MUST come AFTER objects so {key: [a, b]} matches as object first
            # Handles single-line nested arrays within arrays
            'nested-array': {
                'pattern': r'/\[(?:[^\[\]]|\[(?:[^\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\])*\])*\]/',
                'alias': 'language-zolo',
                'greedy': True,
                'inside': {
                    'bracket': {
                        'pattern': r'/[\[\]]/',
                        'alias': 'bracket'
                    },
                    'comma': {
                        'pattern': r'/,/',
                        'alias': 'punctuation'
                    },
                    'string': {
                        'pattern': r'/[^\[\],\s]+(?:\s+[^\[\],\s]+)*/',
                        'alias': 'string'
                    }
                },
                'comment': 'Nested arrays within arrays (e.g., [nested, array, here])'
            },
            # Array items: Process in order - booleans/null (keywords), numbers (pure), strings (catch-all)
            # CRITICAL: String pattern MUST come LAST to catch item1, item2, etc.
            'boolean': {
                'pattern': r'/\b(?:true|false|True|False)\b/',
                'alias': 'boolean',
                'comment': 'Standalone booleans only (case-insensitive)'
            },
            'null': {
                'pattern': r'/\bnull\b/',
                'alias': 'null',
                'comment': 'Standalone null only'
            },
            'number': {
                'pattern': r'/(?<![a-zA-Z0-9_])-?(?:0(?!\d)|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?(?![a-zA-Z0-9_])/',
                'alias': 'number',
                'comment': 'Pure numbers only (not part of identifiers like item1)'
            },
            'string': {
                'pattern': r'/[^\[\],\s]+(?:\s+[^\[\],\s]+)*/',
                'alias': 'string',
                'comment': 'Catch-all (LAST) - matches item1, item2, hello, etc.'
            }
        },
        'comment': 'SSOT: value_emitters.py:emit_array_tokens() depth counter (lines 260-264)'
    })
    
    # SSOT: Dash lists (YAML-style arrays: key:\n  - item1\n  - item2)
    # SSOT: tokenizing_parser.py handles dash lists via handle_dash_list_with_tokens
    # Pattern matches dash-prefixed items after a key with empty value
    # NOTE: This is a simplified pattern - full multiline logic is in SSOT parser
    # Matches both: "- content" and "-" (empty dash for nested lists)
    patterns.append({
        'name': 'dash-list',
        'pattern': r'/(?<=\n)[ \t]*-(?:\s+[^\n]+)?/',
        'alias': 'language-zolo',
        'lookbehind': True,
        'inside': {
            'dash': {
                'pattern': r'/^[ \t]*-\s*/',
                'alias': 'bracket',
                'comment': 'Dash treated as array bracket for visual consistency'
            },
            # CRITICAL: Object MUST come before array to match {key: [a, b]} correctly
            # Inline objects in dash lists (e.g., - {key: value})
            # Simplified pattern: match from { to } with any content except unmatched braces
            # Handles: {simple: value}, {with_array: [a, b]}, {nested: {deep: value}}
            # Strategy: [^{}] | \{[^{}]*\} allows one level of nesting
            'object': {
                'pattern': r'/\{(?:[^{}]|\{[^{}]*\})*\}/',
                'alias': 'language-zolo',
                'greedy': True,
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
                        'pattern': r'/[a-zA-Z][a-zA-Z0-9_]*(?=\s*:)/',
                        'alias': 'property'
                    },
                    'colon': {
                        'pattern': r'/:/',
                        'alias': 'punctuation'
                    },
                    # Nested arrays inside objects in dash lists
                    'array': {
                        'pattern': r'/\[(?:[^\[\]]|\[(?:[^\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\])*\])*\]/',
                        'alias': 'language-zolo',
                        'greedy': True,
                        'inside': {
                            'bracket': {
                                'pattern': r'/[\[\]]/',
                                'alias': 'bracket'
                            },
                            'comma': {
                                'pattern': r'/,/',
                                'alias': 'punctuation'
                            },
                            'string': {
                                'pattern': r'/[^\[\],\s]+(?:\s+[^\[\],\s]+)*/',
                                'alias': 'string'
                            }
                        }
                    },
                    # Primitives BEFORE string (string is catch-all)
                    'boolean': {
                        'pattern': r'/\b(?:true|false|True|False)\b/',
                        'alias': 'boolean'
                    },
                    'null': {
                        'pattern': r'/\bnull\b/',
                        'alias': 'null'
                    },
                    'number': {
                        'pattern': r'/(?<![a-zA-Z0-9_])-?(?:0(?!\d)|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?(?![a-zA-Z0-9_])/',
                        'alias': 'number'
                    },
                    'string': {
                        'pattern': r'/[^{}\[\],:\s]+(?:\s+[^{}\[\],:\s]+)*/',
                        'alias': 'string',
                        'comment': 'String-first: treat all object values as strings (excludes brackets for nested arrays)'
                    }
                }
            },
            # Inline arrays in dash lists (e.g., - [x, y, z])
            # CRITICAL: Array comes AFTER object so {key: [a, b]} matches as object first
            'array': {
                'pattern': r'/\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]/',
                'alias': 'language-zolo',
                'inside': {
                    'bracket': {
                        'pattern': r'/[\[\]]/',
                        'alias': 'bracket'
                    },
                    'comma': {
                        'pattern': r'/,/',
                        'alias': 'punctuation'
                    },
                    'string': {
                        'pattern': r'/[^\[\],\s]+(?:\s+[^\[\],\s]+)*/',
                        'alias': 'string',
                        'comment': 'String-first: treat all non-structural content as strings'
                    }
                }
            },
            # Dash list items: string-first (no boolean/null/number)
            'string': {
                'pattern': r'/[^\s]+(?:\s+[^\s]+)*/',
                'alias': 'string',
                'comment': 'String-first: treat all dash list content as strings'
            }
        },
        'comment': 'SSOT: tokenizing_parser.py:handle_dash_list_with_tokens (multiline YAML lists)'
    })
    
    # SSOT Line 127: Objects BEFORE strings (structural-first)
    # SSOT: value_emitters.py:emit_object_tokens() uses depth counter for nesting (lines 300-304)
    # Pattern matches objects with balanced braces using nested repetition
    # CRITICAL: Must match starting after colon and ending at line end to avoid matching braces in strings
    # NOTE: (str) type hint override handled by separate high-priority pattern in prism_pattern_generator.py
    # MULTILINE: Uses [\s\S] to match any character including newlines
    # BALANCED BRACES: Uses 4-level nested pattern to match balanced {} pairs
    patterns.append({
        'name': 'object',
        'pattern': r'/(?<=:\s*)\{(?:[^{}]|\{(?:[^{}]|\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\})*\})*\}(?=\s*(?:\n|$))/m',
        'alias': 'language-zolo',
        'lookbehind': True,
        'greedy': True,
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
            'type-hint': {
                'pattern': r'/\([^)]+\)(?=\s*:)/',
                'inside': {
                    'type-hint-paren': {
                        'pattern': r'/[()]/',
                        'alias': 'punctuation',
                        'comment': 'SSOT: TokenType.TYPE_HINT_PAREN'
                    },
                    'type-hint-text': {
                        'pattern': r'/[^()]+/',
                        'alias': 'type',
                        'comment': 'SSOT: TokenType.TYPE_HINT'
                    }
                },
                'comment': 'Type hints after properties (only in objects)'
            },
            'colon': {
                'pattern': r'/:/',
                'alias': 'punctuation'
            },
            # Nested structures FIRST (most specific)
            # CRITICAL: No lookbehind needed - we're already inside object context
            # The lookbehind was preventing arrays from matching inside inline objects
            'nested-array': {
                'pattern': r'/\[(?:[^\[\]]|\[(?:[^\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\])*\])*\]/',
                'alias': 'language-zolo',
                'greedy': True,
                'inside': {
                    'bracket': {'pattern': r'/[\[\]]/', 'alias': 'bracket'},
                    'comma': {'pattern': r'/,/', 'alias': 'punctuation'},
                    'boolean': {'pattern': r'/\b(?:true|false|True|False)\b/', 'alias': 'boolean'},
                    'null': {'pattern': r'/\bnull\b/', 'alias': 'null'},
                    'number': {'pattern': r'/(?<![a-zA-Z0-9_])-?(?:0(?!\d)|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?(?![a-zA-Z0-9_])/', 'alias': 'number'},
                    'string': {'pattern': r'/[^\[\],\s]+(?:\s+[^\[\],\s]+)*/', 'alias': 'string'}
                },
                'comment': 'Arrays nested inside objects (no lookbehind - already in object context)'
            },
            'nested-object': {
                'pattern': r'/\{(?:[^{}]|\{(?:[^{}]|\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\})*\})*\}/',
                'alias': 'language-zolo',
                'greedy': True,
                'inside': 'Prism.languages.zolo',
                'comment': 'Objects nested inside objects (recursive - no lookbehind needed in object context)'
            },
            # Object values: Process in order - booleans/null (keywords), numbers (pure), strings (catch-all)
            # CRITICAL: String pattern MUST come LAST
            # NOTE: No lookbehind needed - these patterns are already inside object context
            'boolean': {
                'pattern': r'/\b(?:true|false|True|False)\b/',
                'alias': 'boolean',
                'comment': 'Standalone booleans only (case-insensitive)'
            },
            'null': {
                'pattern': r'/\bnull\b/',
                'alias': 'null',
                'comment': 'Standalone null only'
            },
            'number': {
                'pattern': r'/(?<![a-zA-Z0-9_])-?(?:0(?!\d)|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?(?![a-zA-Z0-9_])/',
                'alias': 'number',
                'comment': 'Pure numbers only (not part of identifiers)'
            },
            'string': {
                'pattern': r'/[^{},:\s]+(?:\s+[^{},:\s]+)*/',
                'alias': 'string',
                'comment': 'Catch-all (LAST) - matches any value'
            }
        },
        'comment': 'SSOT: value_emitters.py:emit_object_tokens() depth counter (lines 300-304)'
    })
    
    # SSOT Line 132: Booleans (standalone only)
    # NOTE: (str) type hint override handled by separate high-priority pattern in prism_pattern_generator.py
    # SSOT: value_emitters.py:140 uses value.lower() - accepts both true/false and True/False
    patterns.append({
        'name': 'boolean',
        'pattern': r'/(?<=:\s+)(?:true|false|True|False)(?=\s*$)/m',
        'alias': 'boolean',
        'lookbehind': True,
        'comment': 'SSOT: value_emitters.py:140 - Case-insensitive true/false'
    })
    
    # SSOT Line 137: Numbers
    # Regex derived from validators.py:is_valid_number() anti-quirk check (line 190)
    # Pattern: -?(?:0(?!\d)|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?
    # Breakdown:
    #   -? = optional minus
    #   (?:0(?!\d)|[1-9]\d*) = either '0' not followed by digit, OR 1-9 followed by digits
    #   (?:\.\d+)? = optional decimal part
    #   (?:[eE][+-]?\d+)? = optional scientific notation
    # Anti-quirk: Rejects 00123, 0123, 01 (leading zeros)
    # NOTE: (str) type hint override handled by separate high-priority pattern in prism_pattern_generator.py
    patterns.append({
        'name': 'number',
        'pattern': r'/(?<=:\s+)-?(?:0(?!\d)|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?(?=\s*$)/m',
        'alias': 'number',
        'lookbehind': True,
        'comment': 'SSOT: validators.py:is_valid_number() - No leading zeros (anti-quirk)'
    })
    
    # SSOT Line 142: Null (standalone only)
    patterns.append({
        'name': 'null',
        'pattern': r'/(?<=:\s+)null(?=\s*$)/m',
        'alias': 'null',
        'lookbehind': True,
        'comment': 'SSOT: value_emitters.py:142 - Standalone null only'
    })
    
    # SSOT Lines 154-172: Specialized strings (timestamps, versions, ratios)
    # These are checked BEFORE generic strings
    patterns.extend([
        {
            'name': 'timestamp-string',
            'pattern': r'/(?<=:\s+)\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^\s]*/m',
            'alias': 'string',
            'lookbehind': True,
            'comment': 'SSOT: value_emitters.py:155 - ISO timestamp strings'
        },
        {
            'name': 'time-string',
            'pattern': r'/(?<=:\s+)\d{2}:\d{2}(?::\d{2})?(?=\s*$)/m',
            'alias': 'string',
            'lookbehind': True,
            'comment': 'SSOT: value_emitters.py:160 - Time strings (HH:MM or HH:MM:SS)'
        },
        {
            'name': 'version-string',
            'pattern': r'/(?<=:\s+)\d+\.\d+(?:\.\d+|\.\*)+(?=\s*$)/m',
            'alias': 'string',
            'lookbehind': True,
            'comment': 'SSOT: value_emitters.py:165 - Version strings (1.0.0, 2.*.3)'
        },
        {
            'name': 'ratio-string',
            'pattern': r'/(?<=:\s+)\d{1,3}:\d{1,3}(?=\s*$)/m',
            'alias': 'string',
            'lookbehind': True,
            'comment': 'SSOT: value_emitters.py:170 - Ratio strings (16:9, 4:3)'
        }
    ])
    
    # SSOT Line 174: String (DEFAULT - MUST BE LAST)
    # This is the fallback for everything else
    # Includes escape sequence highlighting inside strings
    # Allow zero or more spaces after colon (e.g., "key:value" or "key: value")
    patterns.append({
        'name': 'string-unquoted',
        'pattern': r'/(?<=:\s*)\S+(?:\s+\S+)*/m',
        'alias': 'string',
        'lookbehind': True,
        'inside': {
            'escape-sequence': {
                'pattern': r'/\\[nrt\\\\"' + r"']|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{4,8}/",
                'alias': 'constant',
                'comment': 'SSOT: value_emitters.py:202-230 - Known escapes only (permissive)'
            }
        },
        'comment': 'SSOT: value_emitters.py:174 - Default string (LAST, catch-all)'
    })
    
    return patterns


def get_value_pattern_priority_map() -> Dict[str, int]:
    """
    Generate priority map for value patterns based on SSOT order.
    
    This ensures optimize_pattern_order() respects the parser's detection order.
    Lower numbers = higher priority (matched first).
    
    Returns:
        Dictionary mapping pattern name to priority (0-100)
    """
    return {
        # Context-specific values (highest priority)
        # zSpark context-aware zPath (zScrapath, zVaFolder only)
        'zspark-zpath-value': 59,    # @.logs after zScrapath - zSpark-specific
        'zpath-value': 60,           # @.path, ~.path - zOS files
        'env-constant-value': 60,    # PROD, DEBUG - zEnv files
        'env-config-value': 60,      # Production, Development
        
        # Quoted strings (before structural but after context-specific)
        'string-quoted': 61,
        
        # Structural patterns (BEFORE primitives and unquoted strings)
        # CRITICAL: This is the key fix - arrays/objects BEFORE strings
        'array': 64,                 # SSOT line 122
        'object': 64,                # SSOT line 127
        
        # Primitives (after structural, before generic strings)
        'boolean': 65,               # SSOT line 132
        'number': 65,                # SSOT line 137
        'null': 65,                  # SSOT line 142
        
        # Specialized strings (after primitives, before generic strings)
        'timestamp-string': 66,      # SSOT line 155
        'time-string': 66,           # SSOT line 160
        'version-string': 66,        # SSOT line 165
        'ratio-string': 66,          # SSOT line 170
        
        # NOTE: escape-sequence is inside string-unquoted, not top-level
        
        # Generic string (LOWEST priority - catch-all)
        'string-unquoted': 70,       # SSOT line 174 - MUST BE LAST
    }


def validate_ssot_alignment() -> bool:
    """
    Validate that generated patterns align with value_emitters.py order.
    
    This is a self-check to ensure the auto-generation is correct.
    
    Returns:
        True if alignment is correct
        
    Raises:
        AssertionError: If patterns don't match SSOT order
    """
    patterns = generate_value_patterns_from_ssot()
    priority_map = get_value_pattern_priority_map()
    
    # Check that array comes before string-unquoted
    array_idx = next(i for i, p in enumerate(patterns) if p['name'] == 'array')
    string_idx = next(i for i, p in enumerate(patterns) if p['name'] == 'string-unquoted')
    
    assert array_idx < string_idx, \
        f"SSOT violation: array (idx {array_idx}) must come BEFORE string-unquoted (idx {string_idx})"
    
    # Check that object comes before string-unquoted
    object_idx = next(i for i, p in enumerate(patterns) if p['name'] == 'object')
    
    assert object_idx < string_idx, \
        f"SSOT violation: object (idx {object_idx}) must come BEFORE string-unquoted (idx {string_idx})"
    
    # Check that string-unquoted has highest priority (lowest number in value patterns)
    value_pattern_names = [p['name'] for p in patterns]
    max_priority = max(priority_map.get(name, 50) for name in value_pattern_names)
    
    assert priority_map.get('string-unquoted', 0) == max_priority, \
        f"SSOT violation: string-unquoted must have LOWEST priority (highest number)"
    
    return True


# Self-test on module import
if __name__ == '__main__':
    print("Validating SSOT alignment...")
    validate_ssot_alignment()
    print("✓ SSOT alignment validated")
    
    patterns = generate_value_patterns_from_ssot()
    print(f"✓ Generated {len(patterns)} value patterns from SSOT")
    
    for i, pattern in enumerate(patterns):
        print(f"  {i+1}. {pattern['name']}: {pattern['comment']}")
