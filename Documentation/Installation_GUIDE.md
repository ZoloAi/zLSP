# zLSP Installation Guide

How to install zLSP and wire it into your editors.

## Quick start

```bash
# Install the package (note: zolo-lsp, NOT zlsp)
pip install zolo-lsp

# Install for your editor(s)
zlsp-install-all        # All editors (recommended)
zlsp-install-vim        # Vim/Neovim only
zlsp-install-vscode     # VSCode only
zlsp-install-cursor     # Cursor only

# Verify installation
zlsp verify
```

Open any `.zolo` file and the LSP works automatically.

> **Package name warning:** The PyPI package is **`zolo-lsp`**. A separate, old package named `zlsp` (v1.1.0) exists on PyPI and is **not** this project. Always `pip install zolo-lsp`. After install, the Python import name is `zlsp` and the CLI command is `zlsp` — only the pip name differs.

## Requirements

- **Python 3.8+**
- **pygls 1.3.0+** (LSP framework, installed automatically)
- **lsprotocol 2023.0.0+** (LSP types, installed automatically)

For Vim:
- **Neovim 0.8+** (built-in LSP) OR
- **Vim 9+** with the vim-lsp plugin

For VSCode/Cursor:
- Recent versions (extension targets VSCode engine 1.75+)
- Node.js/npm (the installer fetches `vscode-languageclient` for the generated extension)

## What gets installed

`pip install zolo-lsp` provides:

- the `zlsp` Python package (parser, LSP server, providers, themes, generators)
- `zolo-lsp` — the LSP server command (stdio)
- `zlsp` — the CLI (`verify`, `test`, `server`, `info`, `generate-prism`)
- `zlsp-install-{vim,vscode,cursor,all}` and `zlsp-uninstall-{vim,vscode,cursor,all}`
- `zlsp-generate-prism` — Prism.js bundle regeneration (contributors only; the bundle ships pre-built in the package, see [Prism_GUIDE.md](Prism_GUIDE.md))

## Satellite guides

- [Installation_Guides/pypi_GUIDE.md](Installation_Guides/pypi_GUIDE.md) — PyPI install and editor integration
- [Installation_Guides/from_source_GUIDE.md](Installation_Guides/from_source_GUIDE.md) — clone and editable install for contributors
- [Installation_Guides/verify_GUIDE.md](Installation_Guides/verify_GUIDE.md) — health checks and manual verification
- [Installation_Guides/troubleshooting_GUIDE.md](Installation_Guides/troubleshooting_GUIDE.md) — common issues and uninstall

## Next steps

- Try the examples: [basic.zolo](../examples/basic.zolo), [advanced.zolo](../examples/advanced.zolo)
- Editor specifics: [Editors_GUIDE.md](Editors_GUIDE.md)
- How it works: [Architecture_GUIDE.md](Architecture_GUIDE.md)
