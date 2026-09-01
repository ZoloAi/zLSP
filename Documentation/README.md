# zLSP Documentation

Documentation map for zLSP — the Language Server Protocol implementation for `.zolo` files.

Each `*_GUIDE.md` file is a hub; its `*_Guides/` folder holds focused satellite guides.

## Guides

| Hub | Satellites | Covers |
|-----|-----------|--------|
| [Installation_GUIDE.md](Installation_GUIDE.md) | [Installation_Guides/](Installation_Guides/) | Installing from PyPI or source, verifying, troubleshooting |
| [Architecture_GUIDE.md](Architecture_GUIDE.md) | [Architecture_Guides/](Architecture_Guides/) | Parser routing, providers, token registry, LSP server |
| [Grammar_GUIDE.md](Grammar_GUIDE.md) | [Grammar_Guides/](Grammar_Guides/) | File types, zGate, zRaven, zMenu, diagnostics |
| [Themes_GUIDE.md](Themes_GUIDE.md) | [Themes_Guides/](Themes_Guides/) | Color ledger, semantic token pipeline |
| [Prism_GUIDE.md](Prism_GUIDE.md) | [Prism_Guides/](Prism_Guides/) | Prism.js generation, Bifrost mount, bundle freshness |
| [Editors_GUIDE.md](Editors_GUIDE.md) | [Editors_Guides/](Editors_Guides/) | Vim, VSCode, Cursor, icons and language IDs |
| [CLI_GUIDE.md](CLI_GUIDE.md) | [CLI_Guides/](CLI_Guides/) | `zlsp` command reference |
| [Philosophy_GUIDE.md](Philosophy_GUIDE.md) | — | Design principles behind zLSP |

## Quick facts

- **Install:** `pip install zolo-lsp` (NOT `pip install zlsp` — that is an old, unrelated package on PyPI)
- **Import:** `from zlsp.parser import load, loads, dump, dumps`
- **Repo:** [github.com/ZoloAi/zLSP](https://github.com/ZoloAi/zLSP)
- **Current version:** 1.2.0

## Source-of-truth pointers

The code is always the SSOT. When docs and code disagree, trust:

- Parser API and routing — `zlsp/parser/` (`parser_service.py`, `parser.py`)
- File types — `zlsp/parser/zvaf/file_type_detector.py`
- Token types and key sets — `zlsp/token_types.py`, `zlsp/token_registry.py`
- Colors — `zlsp/themes/zolo_default.yaml`
- CLI — `zlsp/cli/argument_parser.py`
- Prism generation — `zlsp/generators/` (has its own co-located dev docs)
