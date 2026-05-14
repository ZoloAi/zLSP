# Type Hint Parentheses Token Emission Fix

## Problem

The LSP server was NOT emitting separate `TYPE_HINT_PAREN` tokens for the `(` and `)` characters in type hints like `port(int)`. Instead, it was emitting a single `TYPE_HINT` token for the entire `(int)` string.

**Evidence from LSP output:**
```
Token: type=TokenType.TYPE_HINT, char=8-12  # Covers "(int)" as one token
```

This caused:
1. **Inconsistent colors across editors**: Cursor showed faded blue, VSCode showed light yellow, Vim showed light yellow, Prism showed white (correct)
2. **Theme SSOT not applied**: The `typeHintParen: white` setting in `zolo_default.yaml` was ignored
3. **Double black flag**: Different colors in different IDEs despite having a single source of truth

## Root Cause

Three functions were missing `TYPE_HINT_PAREN` token emissions:

1. `zlsp/zlsp/parser/core/key_value_parser.py::parse_key_and_emit_root()`
2. `zlsp/zlsp/parser/core/key_value_parser.py::parse_key_and_emit_nested()`
3. `zlsp/zlsp/parser/zvaf/key_value_wrapper.py::_emit_type_hint()`

These functions only emitted the `TYPE_HINT` token for the text inside the parentheses, but did NOT emit `TYPE_HINT_PAREN` tokens for the `(` and `)` characters.

## Solution

Modified all three functions to emit three separate tokens for type hints:

```python
# Before (WRONG):
if type_hint:
    hint_start = key_start + len(clean_key) + 1  # +1 for opening paren
    emitter.emit(line_num, hint_start, len(type_hint), TokenType.TYPE_HINT)

# After (CORRECT):
if type_hint:
    # Emit opening paren
    paren_pos = key_start + len(clean_key)
    emitter.emit(line_num, paren_pos, 1, TokenType.TYPE_HINT_PAREN)
    
    # Emit type hint text
    hint_start = paren_pos + 1
    emitter.emit(line_num, hint_start, len(type_hint), TokenType.TYPE_HINT)
    
    # Emit closing paren
    close_paren_pos = hint_start + len(type_hint)
    emitter.emit(line_num, close_paren_pos, 1, TokenType.TYPE_HINT_PAREN)
```

## Expected LSP Output After Fix

```
Token: type=TokenType.NESTED_KEY, char=4-7     # "port"
Token: type=TokenType.TYPE_HINT_PAREN, char=7-8  # "("
Token: type=TokenType.TYPE_HINT, char=8-11      # "int"
Token: type=TokenType.TYPE_HINT_PAREN, char=11-12 # ")"
Token: type=TokenType.COLON, char=12-13         # ":"
```

## Verification

After restarting the LSP server (reload Cursor/VSCode/Vim):

1. **Cursor**: Parentheses should be white (#ffffff)
2. **VSCode**: Parentheses should be white (#ffffff)
3. **Vim**: Parentheses should be white (ctermfg=15 guifg=#ffffff)
4. **Prism**: Already correct (white)

## Key Principle

**All syntax elements must be tokenized separately by the LSP server**. If the parser doesn't emit distinct tokens for distinct visual elements, the theme SSOT cannot apply different colors to them.

The token emission is the **first layer** of the SSOT architecture:
1. **Parser** emits tokens (TYPE_HINT_PAREN, TYPE_HINT, COLON, etc.)
2. **Theme YAML** defines colors for each token type
3. **Generators** (Vim, VSCode, Prism) read from theme and apply colors

If layer 1 (parser) is wrong, layers 2-3 cannot fix it.
