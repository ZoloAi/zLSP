# Prism.js Pattern Order Fix

## Problem

Numbers in Prism.js web highlighting were showing as white (default color) instead of orange (#FF8C00), even though the CSS was correct.

**Root cause:** Pattern order in `prism-zolo.js` was wrong. The `string-unquoted` pattern (catch-all for any non-whitespace) was matching BEFORE the `number` pattern, so numbers were being styled as strings.

## Pattern Order Issue

**Before (WRONG):**
```javascript
Prism.languages.zolo = {
    'comment': { ... },
    'root-key': { ... },
    'property': { ... },
    'type-hint': { ... },
    'string-quoted': { ... },
    'string-unquoted': { pattern: /\S+(?:\s+\S+)*/ },  // ← Matches numbers!
    'number': { pattern: /\b\d+\.?\d*\b/ },            // ← Never reached
    'boolean': { ... },
    'punctuation': { ... }
};
```

**After (CORRECT):**
```javascript
Prism.languages.zolo = {
    'comment': { ... },
    'root-key': { ... },
    'property': { ... },
    'type-hint': { ... },
    'string-quoted': { ... },
    'number': { pattern: /\b\d+\.?\d*\b/ },            // ← Matches first
    'boolean': { ... },
    'string-unquoted': { pattern: /\S+(?:\s+\S+)*/ },  // ← Catch-all LAST
    'punctuation': { ... }
};
```

## Solution

Modified `zlsp/zlsp/generators/prism_pattern_transformer.py` to set correct priorities in `optimize_pattern_order()`:

```python
priority_order = {
    # ... keys and type hints ...
    'string-quoted': 61,        # Quoted strings (specific)
    'number': 62,               # Numbers (must be before string-unquoted)
    'boolean': 62,              # Booleans (must be before string-unquoted)
    'string-unquoted': 70,      # Unquoted strings (catch-all, MUST BE LAST)
    'punctuation': 100,
}
```

Added explicit entries for `string-quoted` and `string-unquoted` with correct priorities to ensure catch-all pattern is always last.

## Key Principle

**In Prism.js, pattern order determines matching precedence.** The first pattern that matches wins. Therefore:

1. **Specific patterns** (numbers, booleans) must come BEFORE catch-all patterns
2. **Catch-all patterns** (unquoted strings) must be LAST
3. The pattern generator's `optimize_pattern_order()` function is the SSOT for pattern ordering

## Verification

After regenerating with `python3 -m zlsp.generators.generate_prism_zolo`:

- Numbers (8080, 30, 100) should be orange (#FF8C00)
- Booleans (true, false) should be blue
- Unquoted strings should be cream
- Pattern order in generated `prism-zolo.js` should match the priority order

## Files Modified

- `zlsp/zlsp/generators/prism_pattern_transformer.py` - Added explicit priorities for string patterns
- Regenerated all 6 Prism.js files (zolo, zspark, zui, zschema, zconfig, zenv)
