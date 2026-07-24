# zLSP Installation Guide

Complete installation and troubleshooting guide for zLSP.

## Quick Start

```bash
# Install the package — note the name: zolo-lsp
pip install zolo-lsp

# Install for your editor(s)
zlsp-install-all        # All editors + Prism.js (recommended)
zlsp-install-vim        # Vim/Neovim only
zlsp-install-vscode     # VSCode only
zlsp-install-cursor     # Cursor only

# Verify installation
zlsp verify
```

That's it — open any `.zolo` file and the LSP works automatically.

> **Naming note:** the *package* name is **`zolo-lsp`** but the *import* name
> is `zlsp` (there is no `zlsp` package on PyPI — `pip install zlsp` fails):
>
> ```python
> from zlsp.parser import loads
> ```

## Requirements

- **Python 3.8+**
- **pygls 1.3.0+** and **lsprotocol 2023.0.0+** (installed automatically)

For editors:

| Editor | Requirement |
|--------|-------------|
| Neovim (recommended) | 0.8+ — built-in LSP, zero config |
| Vim | 9.0+ with the `vim-lsp` plugin; Vim 8 gets fallback syntax only |
| VSCode / Cursor | any recent version — built-in LSP |

## Installation Methods

### From PyPI (most users)

```bash
pip install zolo-lsp
```

Installs the `zlsp` Python package, the `zolo-lsp` LSP server command, the
`zlsp` CLI, and the `zlsp-install-*` / `zlsp-uninstall-*` editor commands.

### From source (contributors)

```bash
git clone https://github.com/ZoloAi/zLSP.git
cd zLSP
pip install -e .
```

Editable install — modify code, see changes immediately (restart the LSP
server / reload the editor to pick them up).

## Editor Integration

```bash
zlsp-install-all      # Vim + VSCode + Cursor + Prism.js regeneration
```

Or per editor: `zlsp-install-vim` / `zlsp-install-vscode` / `zlsp-install-cursor`.

**What gets installed:**

- **Vim/Neovim** (`~/.vim/` or `~/.config/nvim/`): `ftdetect/`, `ftplugin/`,
  `after/ftplugin/`, `syntax/`, `indent/` files for `.zolo`.
- **VSCode** (`~/.vscode/extensions/zolo-lsp-<version>/`): extension manifest,
  LSP client, generated TextMate syntaxes and semantic color theme.
- **Cursor** (`~/.cursor/extensions/zolo-lsp-<version>/`): same structure as VSCode.

The installer **removes all old `zolo-lsp-*` extension versions** before
installing the new one, so generated files are always regenerated from the
current theme SSOT — no stale-version color drift.

## Verification

```bash
zlsp verify             # health check
zlsp verify --verbose   # detailed diagnostics
```

Checks Python version, dependencies, parser round-trip, LSP server
availability, semantic tokenizer, and detected editor integrations.

Manual spot checks:

```bash
which zolo-lsp                      # LSP server command on PATH
python3 -c "from zlsp.parser import loads; print(loads('key: value'))"
# → {'key': 'value'}
ls ~/.vscode/extensions/ | grep zolo-lsp   # extension present (versioned dir)
```

Then open `examples/basic.zolo` (in the repo) in your editor: highlighting,
hover docs, and live diagnostics should all be active.

## Editor-Specific Setup

### Neovim (0.8+)

Works out of the box after `zlsp-install-vim`. Optional tuning in `init.lua`:

```lua
vim.diagnostic.config({ float = { border = "rounded" } })
```

### Vim 9+ (vim-lsp)

Install the plugin (vim-plug shown; Vundle/Pathogen equally fine):

```vim
call plug#begin()
Plug 'prabirshrestha/vim-lsp'
call plug#end()
```

`:PlugInstall`, restart, then run `zlsp-install-vim` again to wire the client.
Vim 8 and older: fallback syntax highlighting only (no LSP) — upgrade to Vim 9+
or Neovim.

### VSCode / Cursor

Run the installer, restart the editor, open a `.zolo` file, and check the
status bar for "Zolo Language Server". Hover a key to confirm docs appear.

## Troubleshooting

**LSP server not found**

```bash
pip show zolo-lsp          # is it installed?
which zolo-lsp             # on PATH?
export PATH="$HOME/.local/bin:$PATH"   # common fix
```

**No syntax highlighting**

- Vim: `:set filetype?` should show `zolo` — if not, rerun `zlsp-install-vim`.
- VSCode/Cursor: check the Zolo LSP extension is enabled, then
  "Developer: Reload Window".

**Module import errors / wrong package**

```bash
pip install --force-reinstall zolo-lsp
zlsp verify
```

**LSP not connecting (Vim)** — `:LspInfo` (Neovim) / `:LspStatus` (Vim 9+)
should show `zolo-lsp` attached; if not, rerun the installer.

**Extension errors (VSCode/Cursor)** — View → Output → "Zolo Language Server"
shows the server log (zLSP logs to stderr, standard for LSP servers). If the
server can't find Python, set `python.defaultInterpreterPath` in settings.

## Uninstall

```bash
zlsp-uninstall-all      # remove all editor integrations
pip uninstall zolo-lsp  # remove the package + CLI commands
```

Per editor: `zlsp-uninstall-vim` / `zlsp-uninstall-vscode` / `zlsp-uninstall-cursor`.

## Theme Customization (advanced)

The canonical theme is `zlsp/themes/zolo_default.yaml` — the single source of
truth every editor's colors are generated from. See
[Themes_GUIDE](Themes_GUIDE.md) before touching it; per-editor color overrides
are deliberately not supported (that's the SSOT contract).

## Next Steps

- [Documentation index](README.md) — all hubs
- [Architecture_GUIDE](Architecture_GUIDE.md) — how the pieces fit
- [CLI_GUIDE](CLI_GUIDE.md) — the `zlsp` command reference

Issues: [github.com/ZoloAi/zLSP/issues](https://github.com/ZoloAi/zLSP/issues)
