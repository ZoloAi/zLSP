# zLSP Installation Guide

Complete installation and troubleshooting guide for zLSP.

## Quick Start

```bash
# Install zlsp
pip install zlsp

# Install for your editor(s)
zlsp-install-all        # All editors + Prism.js (recommended)
zlsp-install-vim        # Vim/Neovim only
zlsp-install-vscode     # VSCode only
zlsp-install-cursor     # Cursor only
zlsp-generate-prism     # Prism.js only (if not using install-all)

# Verify installation
zlsp verify
```

That's it! Open any `.zolo` file and the LSP will work automatically.

## Requirements

- **Python 3.8+**
- **pygls 1.3.0+** (LSP framework)
- **lsprotocol 2023.0.0+** (LSP types)

For Vim:
- **Neovim 0.8+** (built-in LSP) OR
- **Vim 9+** with vim-lsp plugin

For VSCode/Cursor:
- **VSCode 1.50+** OR **Cursor** (any recent version)
- Both have built-in LSP support

### Editors

**Neovim** (Recommended)
- Neovim 0.8+ has built-in LSP support
- Zero configuration needed

**Vim**
- Vim 9.0+ works with vim-lsp plugin
- Vim 8 and older: fallback syntax only (no LSP)

**VSCode/Cursor**
- Any recent version (1.50+)
- Built-in LSP support

## Installation Methods

### Method 1: From PyPI (Production)

**Recommended for most users:**

```bash
pip install zlsp
```

This installs:
- `zlsp` Python package
- `zolo-lsp` LSP server command
- `zlsp-install-*` editor integration commands
- `zlsp verify` health check command

### Method 2: From Source (Development)

**For contributors or local development:**

```bash
cd /path/to/ZoloMedia/zlsp
pip install -e .
```

Editable install allows you to modify code and see changes immediately.

### Method 3: From Git

**Latest development version:**

```bash
pip install git+https://github.com/ZoloAi/ZoloMedia.git#subdirectory=zlsp
```

## Editor Integration

### Install for All Editors

```bash
zlsp-install-all
```

Automatically installs zLSP for **Vim**, **VSCode**, and **Cursor**, plus generates **Prism.js** files for web syntax highlighting.

**What it does:**
1. Installs Vim integration (`~/.vim/`)
2. Installs VSCode extension (`~/.vscode/extensions/`)
3. Installs Cursor extension (`~/.cursor/extensions/`)
4. Generates Prism.js patterns (6 JS files)
5. Generates Prism.js CSS theme

This is the **recommended command** for full zlsp setup.

### Install for Specific Editors

```bash
# Vim/Neovim
zlsp-install-vim

# VSCode
zlsp-install-vscode

# Cursor
zlsp-install-cursor
```

### What Gets Installed

**Vim/Neovim** (`~/.vim/` or `~/.config/nvim/`):
```
ftdetect/zolo.vim       # Auto-detect .zolo files
ftplugin/zolo.vim       # Basic settings (comments, indent)
after/ftplugin/zolo.vim # LSP client setup
syntax/zolo.vim         # Fallback syntax highlighting
indent/zolo.vim         # Indentation rules
```

**VSCode** (`~/.vscode/extensions/`):
```
zolo-lsp-1.0.0/         # Extension directory
├── package.json        # Extension manifest
├── client.js           # LSP client
└── syntaxes/           # Syntax highlighting
```

**Cursor** (`~/.cursor/extensions/`):
```
zolo-lsp-1.0.0/         # Extension directory
(same structure as VSCode)
```

## Verification

### Health Check

After installation, verify everything works:

```bash
zlsp verify
```

This checks:
- [ok] Python version (3.8+)
- [ok] Core dependencies (pygls, lsprotocol)
- [ok] Parser functionality
- [ok] LSP server availability
- [ok] Semantic tokenizer
- [ok] Editor integrations (Vim, VSCode, Cursor detected)

For detailed diagnostics:
```bash
zlsp verify --verbose
```

### Manual Verification

```bash
# 1. Check Python package
python3 -c "import core; print(core.__version__)"

# 2. Check LSP server command
which zolo-lsp
zolo-lsp --help

# 3. Check editor install commands
which zlsp-install-vim
which zlsp-install-vscode
which zlsp-install-cursor

# 4. Test parser
python3 -c "from core.parser import loads; print(loads('key: value'))"
# Expected: {'key': 'value'}

# 5. Check Vim files
ls ~/.vim/ftdetect/zolo.vim
ls ~/.vim/after/ftplugin/zolo.vim

# 6. Check VSCode extension
ls ~/.vscode/extensions/zolo-lsp-1.0.0/

# 7. Check Cursor extension
ls ~/.cursor/extensions/zolo-lsp-1.0.0/
```

### Test in Editor

**If you cloned the repo**, open `zlsp/examples/basic.zolo` in your editor.

**Or download directly:**
- [basic.zolo](https://github.com/ZoloAi/ZoloMedia/blob/main/zlsp/examples/basic.zolo) (27 lines, simple)
- [advanced.zolo](https://github.com/ZoloAi/ZoloMedia/blob/main/zlsp/examples/advanced.zolo) (700+ lines, all features)

**If you are using terminal**, download a test file and open with Vim:

```bash
curl -O https://raw.githubusercontent.com/ZoloAi/ZoloMedia/main/zlsp/examples/basic.zolo
vim basic.zolo
```

**Expected behavior:**
- Syntax highlighting active
- Type hints recognized
- Hover over keys shows documentation
- Error detection for invalid syntax

## Editor-Specific Setup

### Neovim (Built-in LSP)

Neovim 0.8+ works automatically. No additional setup needed.

**Optional:** Customize LSP behavior in `~/.config/nvim/init.lua`:
```lua
-- Example: Show diagnostics in floating window
vim.diagnostic.config({
  float = { border = "rounded" },
})
```

### Vim 9+ (with vim-lsp)

Vim 9+ requires the vim-lsp plugin for LSP features.

**Using vim-plug:**
```vim
" Add to ~/.vimrc
call plug#begin()
Plug 'prabirshrestha/vim-lsp'
call plug#end()
```

Then run `:PlugInstall` and restart Vim.

**Using Vundle:**
```vim
" Add to ~/.vimrc
Plugin 'prabirshrestha/vim-lsp'
```

Then run `:PluginInstall` and restart Vim.

**Using Pathogen:**
```bash
cd ~/.vim/bundle
git clone https://github.com/prabirshrestha/vim-lsp.git
```

After installing vim-lsp, run `zlsp-install-vim` again to configure it.

### Vim 8 and Older

Vim 8 and older don't support LSP.

**What works:**
- Basic syntax highlighting (fallback)
- File type detection
- Indentation

**What doesn't work:**
- Semantic highlighting
- Real-time diagnostics
- Hover information
- Code completion

**Recommendation:** Upgrade to Vim 9+ or switch to Neovim 0.8+

### VSCode

VSCode has built-in LSP support. After running `zlsp-install-vscode`, restart VSCode.

**Verify:**
1. Open a `.zolo` file
2. Check bottom-right status bar for "Zolo Language Server"
3. Hover over keys to see documentation

### Cursor

Cursor (built on VSCode) has built-in LSP support. After running `zlsp-install-cursor`, restart Cursor.

**Verify:**
1. Open a `.zolo` file
2. Check bottom-right status bar for "Zolo Language Server"
3. Hover over keys to see documentation


## Troubleshooting

### Quick Fixes

**Installation issues:**
```bash
# Verify installation
zlsp verify

# Reinstall from scratch
pip uninstall zlsp && pip install zlsp

# Check Python version (need 3.8+)
python3 --version
```

---

### Common Issues

#### LSP server not found

```bash
# Check if installed
pip show zlsp

# Find zolo-lsp command
which zolo-lsp

# If missing, add to PATH
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc
```

#### No syntax highlighting

**Vim/Neovim:**
```vim
:set filetype?  " Should show 'zolo'
```
If wrong, reinstall: `zlsp-install-vim`

**VSCode/Cursor:**
- Check Extensions → "Zolo LSP" is enabled
- Reload window: Cmd+Shift+P → "Developer: Reload Window"

#### Module import errors

```bash
# Wrong Python environment
pip uninstall zlsp
pip install zlsp

# Verify it worked
zlsp verify
```

---

### Vim/Neovim Specific

**LSP not connecting:**
```vim
:LspInfo        " Neovim
:LspStatus      " Vim 9+
```
Should show `zolo-lsp` attached. If not, reinstall: `zlsp-install-vim`

**Vim 8 not supported:**
- Upgrade to Vim 9+ or use Neovim 0.8+

---

### VSCode/Cursor Specific

**Extension not working:**
1. Open Output panel (View → Output)
2. Select "Zolo Language Server" from dropdown
3. Check for errors

**Common fixes:**
```bash
# Reinstall extension
zlsp-uninstall-vscode
zlsp-install-vscode

# Reload window
# Cmd+Shift+P → "Developer: Reload Window"
```

**Extension not appearing:**
- Check `~/.vscode/extensions/zolo-lsp-1.0.0/` exists
- Or `~/.cursor/extensions/zolo-lsp-1.0.0/` for Cursor
- Reinstall if missing

**LSP server crashes:**
- Check Python path in Output panel
- May need to set `python.defaultInterpreterPath` in settings.json

**Multiple Python versions:**
- Extension uses system Python
- If using conda/venv, may need to set interpreter path
- Settings → Python: Default Interpreter Path

## Uninstallation

### Remove Python Package

```bash
pip uninstall zlsp
```

This removes the Python package and all command-line tools.

### Remove Editor Integrations

**Vim/Neovim:**
```bash
# Automated uninstall
zlsp-uninstall-vim

# Or manual removal:
rm ~/.vim/ftdetect/zolo.vim
rm ~/.vim/ftplugin/zolo.vim
rm ~/.vim/after/ftplugin/zolo.vim
rm ~/.vim/syntax/zolo.vim
rm ~/.vim/indent/zolo.vim

# Neovim:
rm ~/.config/nvim/ftdetect/zolo.vim
rm ~/.config/nvim/ftplugin/zolo.vim
rm ~/.config/nvim/after/ftplugin/zolo.vim
rm ~/.config/nvim/syntax/zolo.vim
rm ~/.config/nvim/indent/zolo.vim
```

**VSCode:**
```bash
# Automated uninstall
zlsp-uninstall-vscode

# Or manual removal:
rm -rf ~/.vscode/extensions/zolo-lsp-1.0.0/
```

**Cursor:**
```bash
# Automated uninstall
zlsp-uninstall-cursor

# Or manual removal:
rm -rf ~/.cursor/extensions/zolo-lsp-1.0.0/
```

**Uninstall from all editors:**
```bash
zlsp-uninstall-all
```

## Advanced Configuration

### Custom LSP Server Port

By default, zLSP uses stdio for LSP communication (no network port needed).

To use TCP (for remote development):
```bash
# Start server on port 9999
zolo-lsp --port 9999
```

Then configure your editor to connect to `localhost:9999`.

### Theme Customization

zLSP uses `themes/zolo_default.yaml` as the canonical theme.

**To customize colors:**

1. Copy the theme:
   ```bash
   cp ~/.local/lib/python3.*/site-packages/themes/zolo_default.yaml ~/my_theme.yaml
   ```

2. Edit `~/my_theme.yaml` to change colors

3. Tell zlsp to use it:
   ```bash
   export ZLSP_THEME=~/my_theme.yaml
   zolo-lsp
   ```

**Note:** Custom themes are advanced. Most users don't need this.

### Logging and Debugging

**View LSP logs in your editor:**

**VSCode/Cursor:**
- View → Output → Select "Zolo Language Server" from dropdown

**Neovim:**
```vim
:LspLog
```

**Vim 9+:**
- Logs appear in `:messages`

**Note:** zLSP logs to stderr by default (standard for LSP servers). If you'd like persistent file logging as a feature, please [open an issue](https://github.com/ZoloAi/ZoloMedia/issues) for future versions.

## Next Steps

After successful installation:

1. **Read the main README:** [README.md](../README.md) for feature overview

2. **Try examples:**
   - [basic.zolo](../examples/basic.zolo) - Simple syntax
   - [advanced.zolo](../examples/advanced.zolo) - Real-world config

3. *Explore(!)* how **`.zolo`** files and **zLSP** integrate into the ***ZoloMedia Ecosystem***: [zOS README](../../zOS/README.md)

5. **Architecture deep dive:** [ARCHITECTURE.md](ARCHITECTURE.md)

## Support

**Issues and Questions:**
- GitHub Issues: [ZoloMedia/issues](https://github.com/ZoloAi/ZoloMedia/issues)
- Check existing issues before creating new ones

**Documentation:**
- Main README: [README.md](../README.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- File Types: [FILE_TYPES.md](FILE_TYPES.md)

**Community:**
- Star the repo to show support
- Share your `.zolo` use cases

---

## FAQ

**Q: Do I need to restart my editor after installation?**
A: Usually yes. VSCode/Cursor need restart. Vim/Neovim can reload with `:edit` or restart.

**Q: Can I use zlsp without an editor (CLI only)?**
A: Yes! Import the parser directly:
```python
from core.parser import loads, dumps
data = loads("key: value")
```

**Q: Does zlsp work on Windows?**
A: Python package works on Windows. Editor integrations are primarily tested on macOS/Linux.

**Q: Can I use multiple versions of zlsp?**
A: Not recommended. Uninstall old version first: `pip uninstall zlsp`

**Q: Why is it called zolo-lsp instead of zlsp?**
A: The LSP server command is `zolo-lsp`, the Python package is `zlsp`. This avoids confusion.

**Q: Do I need internet to use zlsp?**
A: No. After installation, zlsp works completely offline.
