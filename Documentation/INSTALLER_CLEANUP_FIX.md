# Installer Cleanup Fix

## Problem 1: Incomplete Extension Cleanup

The installer was only removing the specific versioned extension directory (e.g., `zolo-lsp-1.1.0`) but not cleaning up all old versions. This could lead to:

1. Multiple old extension versions accumulating
2. Outdated static files (like `semantic-colors.json`) not being regenerated
3. Theme changes not fully propagating to all editors

## Problem 2: Missing Token Mappings in Generators

The Vim generator was missing `colon` and `comma` token mappings, causing these tokens to fall back to default colors instead of using the theme SSOT. This broke the principle that **all colors must come from `zolo_default.yaml`**.

## Solution 1: Complete Extension Cleanup

Modified `zlsp/zlsp/editors/_shared/vscode_base.py` to remove **ALL** old `zolo-lsp-*` directories before installing the new version:

```python
# Remove ALL old zolo-lsp versions (not just current version)
for old_ext in self.extensions_dir.glob('zolo-lsp-*'):
    if old_ext.is_dir():
        print(f"  → Removing old version: {old_ext.name}")
        shutil.rmtree(old_ext)
```

## Solution 2: Add Missing Token Mappings

Modified `zlsp/zlsp/themes/generators/vim.py` to include `colon` and `comma` in the token mapping:

```python
token_mapping = {
    # ... other tokens ...
    'colon': 'LspSemanticColon',
    'comma': 'LspSemanticComma',
    # ... other tokens ...
}
```

This ensures Vim reads colon/comma colors from the theme SSOT (`zolo_default.yaml`) instead of using fallback colors.

## Benefits

- **Complete regeneration**: All extension files are regenerated from the theme SSOT
- **No stale files**: Old cached files are completely removed
- **Theme consistency**: Color changes propagate correctly to all editors
- **Clean state**: Each install starts with a clean slate

## Verification

After the fix, all generated files now correctly reflect theme changes:

1. **Cursor settings.json**: `typeHintParen: #ffffff`, `typeHint: #a89cc4`, `colon: #ffffff`
2. **Vim colors**: 
   - `LspSemanticTypeHintParen ctermfg=15 guifg=#ffffff`
   - `LspSemanticColon ctermfg=15 guifg=#ffffff`
   - `LspSemanticComma ctermfg=227 guifg=#ffff5f`
3. **Prism.js CSS**: 
   - `.token.type-hint-paren { color: #ffffff !important; }`
   - `.token.punctuation { color: #ffffff !important; }`

## Key Principle

**All colors must come from the theme SSOT (`zolo_default.yaml`)**. If a token type exists in the theme but isn't in a generator's token mapping, it will fall back to default colors, breaking consistency across editors.

## Usage

Simply run the installer as usual:

```bash
zlsp-install-all
# or
zlsp-install-cursor
zlsp-install-vim
zlsp-install-vscode
```

The installer will now automatically clean up all old versions before installing.
