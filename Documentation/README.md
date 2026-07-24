# zLSP Documentation

Technical documentation for **zLSP** — the Language Server Protocol implementation
for `.zolo` declarative files. Each hub covers one domain; start with the one that
matches your question.

| Hub | Covers |
|-----|--------|
| [Installation_GUIDE](Installation_GUIDE.md) | Install (`pip install zolo-lsp`), editor setup, verification, troubleshooting, uninstall |
| [Architecture_GUIDE](Architecture_GUIDE.md) | The live module tree: dual-path parser routing, providers, token registry, LSP server |
| [Grammar_GUIDE](Grammar_GUIDE.md) | File-type detection (zSpark/zEnv/zUI/zConfig/zSchema/zRaven), special blocks, zGate, diagnostics |
| [Themes_GUIDE](Themes_GUIDE.md) | The theme SSOT (`zolo_default.yaml`), token→color ledger, generator pipeline |
| [Prism_GUIDE](Prism_GUIDE.md) | Web highlighting: packaged Prism bundle, `bifrost_prism_dir()`, regeneration |
| [Editors_GUIDE](Editors_GUIDE.md) | Vim/Neovim, VSCode, Cursor integrations; language ids; installer behavior |
| [CLI_GUIDE](CLI_GUIDE.md) | `zlsp verify / test / server / info / generate-prism` reference |
| [Philosophy_GUIDE](Philosophy_GUIDE.md) | Why zLSP exists: SSOT, string-first, generated grammars |

**Orientation:**
- New user? [Installation_GUIDE](Installation_GUIDE.md) → open a `.zolo` file → done.
- Contributor? [Architecture_GUIDE](Architecture_GUIDE.md) first, then the domain hub you're touching.
- Coming from zOS/zBifrost? [Prism_GUIDE](Prism_GUIDE.md) explains how the web bundle ships.

**Package facts (SSOT):** PyPI package **`zolo-lsp`** (current: 1.2.0) · import as `zlsp` ·
repo [github.com/ZoloAi/zLSP](https://github.com/ZoloAi/zLSP) · Python 3.8+.

> **Naming note:** the *package* is `zolo-lsp`, the *import* is `zlsp`
> (`from zlsp.parser import loads`). There is no `zlsp` package on PyPI —
> `pip install zlsp` simply fails.
