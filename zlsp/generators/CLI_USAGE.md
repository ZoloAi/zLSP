# Prism.js Generation CLI

Quick reference for generating Prism.js syntax highlighting files.

## Commands

### Generate Everything (Recommended)

```bash
zlsp generate-prism
```

Generates:
- **6 JS pattern files** (from parser SSOT)
  - `prism-zolo.js`, `prism-zspark.js`, `prism-zui.js`, `prism-zschema.js`, `prism-zconfig.js`, `prism-zenv.js`
- **1 CSS theme file** (from theme YAML)
  - `prism-zolo-theme.css`

Output locations:
- `zlsp/generated/` (canonical source)
- `zOS/bifrost/src/syntax/` (dev reference)
- `zCloud/static/js/` (runtime - served by zServer)
- `zCloud/static/css/` (runtime - served by zServer)

### Generate JS Patterns Only

```bash
zlsp generate-prism --patterns-only
```

Generates **only** the 6 JS language files from parser SSOT.

Use when:
- Parser rules changed (KeyDetector, TokenRegistry)
- Token types added/modified
- File type detection logic changed

### Generate CSS Theme Only

```bash
zlsp generate-prism --css-only
```

Generates **only** the CSS theme from theme YAML.

Use when:
- Color scheme changed (zolo_default.yaml)
- Token color mappings changed
- No parser changes

## Comparison with Other Commands

| Command | Purpose | Installs to |
|---------|---------|-------------|
| `zlsp-install-all` | All editors + Prism.js | All locations below |
| `zlsp-install-vim` | Vim LSP client | `~/.vim/` |
| `zlsp-install-vscode` | VSCode extension | `~/.vscode/extensions/` |
| `zlsp-install-cursor` | Cursor extension | `~/.cursor/extensions/` |
| `zlsp-generate-prism` | Web syntax highlighting only | `/static/js/`, `/static/css/` |

**Key insight:** Editors need **installation** (copy configs to user dirs). Prism needs **generation** (create files for web server).

**Note:** `zlsp-install-all` runs both editor installations AND Prism generation, so you get everything in one command.

## Standalone Command

If installed via pip, you also get a standalone command:

```bash
# Same as: zlsp generate-prism
zlsp-generate-prism

# With options
zlsp-generate-prism --patterns-only
zlsp-generate-prism --css-only
zlsp-generate-prism --verbose
```

## Module-Level (Alternative)

If you prefer running modules directly:

```bash
# Patterns
python3 -m zlsp.generators.generate_prism_zolo

# CSS
python3 -m zlsp.themes.generators.prism
```

## When to Regenerate

### Patterns (JS) - Regenerate when:
- ✅ Parser rules change
- ✅ Token types added/modified
- ✅ File type detection changed
- ✅ Any `.py` file in `zlsp/parser/` modified

### CSS Theme - Regenerate when:
- ✅ Theme colors change (`zolo_default.yaml`)
- ✅ Token color mappings change
- ❌ Parser changes (no effect on colors)

### Both - Regenerate when:
- ✅ New token types need colors
- ✅ Preparing for release

## Integration with Workflow

```bash
# Development cycle
vim zlsp/parser/core/key_detector.py  # Modify parser
zlsp test --unit                      # Run tests
zlsp generate-prism                   # Regenerate Prism
zserver restart                       # Restart web server
# Browser: Hard refresh (Cmd+Shift+R)

# Release preparation
zlsp generate-prism                   # Regenerate all
zlsp test                             # Run full test suite
git add zlsp/generated/ zCloud/static/
git commit -m "Regenerate Prism files"
```

## Troubleshooting

### Command not found: `zlsp`

**Solution:** Install zlsp or use module form:
```bash
pip install -e .
# OR
python3 -m zlsp.cli.prism_generator
```

### Permission errors writing to `/static/`

**Solution:** Check directory permissions or run from correct location:
```bash
cd /Users/galnachshon/Projects/ZoloMedia/zlsp
zlsp generate-prism
```

### Changes not visible in browser

**Solution:**
1. Verify files generated: `ls zCloud/static/js/prism-*.js`
2. Restart zServer
3. Hard refresh browser (Cmd+Shift+R)
4. Check browser console for errors

## Help

```bash
zlsp generate-prism --help
```

Shows all available options and descriptions.
