# SSOT-Based Prism Pattern Generation

**Status:** ✅ Implemented (Phase 4.7)

## Overview

Prism.js syntax highlighting patterns are now **auto-generated from the parser's SSOT** to ensure highlighting matches parser behavior exactly. This eliminates manual maintenance and prevents drift between parser logic and syntax highlighting.

## Architecture

### Single Source of Truth

**Parser Logic:** `zlsp/parser/core/value_emitters.py:emit_value_tokens()` (lines 18-185)

This function defines the **canonical order** for value detection:

1. Type hints (explicit override)
2. zPath values (`@.path`, `~.path`)
3. **Arrays** (`[...]`) - line 122
4. **Objects** (`{...}`) - line 127
5. Booleans (`true`/`false`)
6. Numbers
7. Null
8. Environment constants
9. Specialized strings (timestamps, versions, ratios)
10. **String (default)** - line 174

### Auto-Generation Pipeline

```
value_emitters.py (SSOT)
         ↓
value_pattern_generator.py (extracts order)
         ↓
prism_pattern_transformer.py (applies priorities)
         ↓
prism_pattern_generator.py (builds patterns)
         ↓
generate_prism_zolo.py (generates JS files)
         ↓
prism-zolo.js, prism-zspark.js, etc.
```

## Key Modules

### 1. `value_pattern_generator.py` (NEW)

**Purpose:** Auto-generate Prism value patterns by mirroring `emit_value_tokens()` logic.

**Key Functions:**
- `generate_value_patterns_from_ssot()` - Extracts patterns in SSOT order
- `get_value_pattern_priority_map()` - Maps pattern names to priorities
- `validate_ssot_alignment()` - Self-check that patterns match parser order

**Critical Fix:** Arrays/objects now have priority 64, **before** string-unquoted (priority 70), ensuring structural-first detection.

### 2. `prism_pattern_transformer.py` (UPDATED)

**Changes:**
- `optimize_pattern_order()` now imports priorities from `value_pattern_generator.py`
- Value pattern priorities are **no longer hardcoded**
- Merges SSOT value priorities with key/structural priorities

### 3. `prism_pattern_generator.py` (UPDATED)

**Changes:**
- `generate_base_patterns()` now calls `generate_value_patterns_from_ssot()`
- Removed manual `transform_string_pattern()`, `transform_number_pattern()`, etc.
- Value patterns are now **auto-generated** from SSOT

## Pattern Order Verification

### Before (Manual, Incorrect)

```javascript
Prism.languages.zolo = {
    'comment': { ... },
    'root-key': { ... },
    'property': { ... },
    'type-hint': { ... },
    'string-quoted': { ... },      // Line 80 - BEFORE arrays/objects ❌
    'number': { ... },
    'boolean': { ... },
    'null': { ... },
    'escape-sequence': { ... },
    'array': { ... },              // Line 96 - AFTER strings ❌
    'object': { ... },             // Line 97 - AFTER strings ❌
    'string-unquoted': { ... }
};
```

**Problem:** Prism would match `"[1, 2, 3]"` as a quoted string instead of an array.

### After (Auto-Generated, Correct)

```javascript
Prism.languages.zolo = {
    'comment': { ... },
    'root-key': { ... },
    'property': { ... },
    'type-hint': { ... },
    'string-quoted': { ... },      // Explicit quotes (high priority)
    'array': { ... },              // Line 45 - BEFORE unquoted strings ✓
    'object': { ... },             // Line 61 - BEFORE unquoted strings ✓
    'boolean': { ... },
    'number': { ... },
    'null': { ... },
    'timestamp-string': { ... },
    'time-string': { ... },
    'version-string': { ... },
    'ratio-string': { ... },
    'escape-sequence': { ... },
    'string-unquoted': { ... }     // Line 124 - LAST (catch-all) ✓
};
```

**Fixed:** Prism now checks arrays/objects **before** unquoted strings, matching parser behavior.

## Usage

### Regenerate All Prism Files

```bash
cd zlsp
python3 -m zlsp.generators.generate_prism_zolo
```

This will:
1. Extract value patterns from SSOT
2. Validate alignment with parser logic
3. Generate 6 Prism language files (zolo, zspark, zui, zschema, zconfig, zenv)
   into `zlsp/generated/` — the single committed output, shipped as package
   data in the wheel. zOS.zServer serves it at `/zsyntax/<version>/` via
   `zlsp.bifrost_prism_dir()`; no copying into other repos.

Commit `zlsp/generated/` together with the grammar change —
`tests/integration/test_prism_patterns.py` fails if the bundle is stale.

### Test SSOT Alignment

```bash
cd zlsp
python3 -m zlsp.generators.value_pattern_generator
```

Output:
```
✓ SSOT alignment validated
✓ Generated 11 value patterns from SSOT
  1. array: SSOT: value_emitters.py:122 - Arrays checked BEFORE strings
  2. object: SSOT: value_emitters.py:127 - Objects checked BEFORE strings
  ...
  11. string-unquoted: SSOT: value_emitters.py:174 - Default string (LAST, catch-all)
```

## Benefits

### 1. Single Source of Truth
- Parser logic = Prism logic
- No manual synchronization needed
- Changes to `value_emitters.py` automatically propagate

### 2. Correct Priority Order
- Arrays/objects checked **before** strings (structural-first)
- Primitives (bool/number/null) in correct order
- Generic strings **last** (catch-all)

### 3. Verifiable Consistency
- `validate_ssot_alignment()` ensures patterns match parser order
- Unit tests can verify Prism highlighting matches parser tokens

### 4. IDE Install Consistency
- Same generation script for all editors (VSCode, Vim, Bifrost)
- Guaranteed identical highlighting across platforms

## Maintenance

### Adding New Value Types

1. Add detection logic to `value_emitters.py:emit_value_tokens()`
2. Add corresponding pattern to `value_pattern_generator.py:generate_value_patterns_from_ssot()`
3. Add priority to `get_value_pattern_priority_map()`
4. Regenerate: `python3 -m zlsp.generators.generate_prism_zolo`

### Modifying Detection Order

1. Update `value_emitters.py:emit_value_tokens()` (SSOT)
2. Update `value_pattern_generator.py` to match
3. Run `validate_ssot_alignment()` to verify
4. Regenerate Prism files

## Testing

### Unit Tests

```bash
pytest zlsp/tests/unit/test_prism_generator.py -v
```

### Browser Tests

Open `zlsp/tests/browser/test_all_languages.html` to visually verify highlighting.

### Alignment Tests

```python
from zlsp.generators.value_pattern_generator import validate_ssot_alignment

# Raises AssertionError if patterns don't match SSOT order
validate_ssot_alignment()
```

## References

- **SSOT:** `zlsp/parser/core/value_emitters.py:emit_value_tokens()` (lines 18-185)
- **Auto-Generation:** `zlsp/generators/value_pattern_generator.py`
- **Priority Mapping:** `zlsp/generators/prism_pattern_transformer.py:optimize_pattern_order()`
- **Pattern Building:** `zlsp/generators/prism_pattern_generator.py:generate_base_patterns()`
- **CLI:** `zlsp/generators/generate_prism_zolo.py`

## Philosophy

**By-Value, String-First, Structural-First:**

1. **Type hints** override everything (explicit intent)
2. **Structural patterns** (arrays/objects) before strings
3. **Primitives** (bool/number/null) before generic strings
4. **Specialized strings** (timestamps, versions) before generic strings
5. **Generic strings** last (catch-all, default)

This ensures:
- Predictable behavior (no YAML-style surprises)
- Correct structural detection (arrays aren't strings)
- Efficient parsing (specific before generic)
- Consistent highlighting (Prism = Parser)

---

**Last Updated:** Phase 4.7 (March 2026)
**Status:** Production-ready, SSOT-aligned
