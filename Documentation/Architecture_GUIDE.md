# zLSP Architecture

**SSOT Language Server, editor-agnostic, string-first.** This guide describes
the **live** module tree (`zlsp/`) — one parser understands `.zolo`; everything
else (LSP features, editor grammars, web highlighting) derives from it.

## The Big Picture

```
                      ┌─────────────────────────────┐
   editor / runtime → │  parser_service.ParserService │  ← THE entry point
                      └──────────────┬──────────────┘
                     file type detected HERE, before parsing
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        BASIC route (generic .zolo)             ZVAF route (zOS types)
        core/ + basic/ only                     core/ + basic/ + zvaf/
        no zVaF code loaded                     modifiers, UI shorthands,
                                                special blocks
                 └───────────────────┬───────────────────┘
                                     ▼
                          ParseResult (data, tokens, diagnostics)
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
        providers/              server/                generators/
        hover, completion,      pygls LSP protocol,    Prism.js patterns
        diagnostics             semantic tokens        (see Prism_GUIDE)
```

**Dual-path routing** is the headline: `ParserService` detects the file type
from the *filename* at the entry point — before any parsing — and basic files
never load or execute zVaF code. Generic configs parse lean; zOS files get the
full extension set.

## Module Tree (live)

```
zlsp/
├── parser/
│   ├── parser.py            ← public API (tokenize / load / loads / dump / dumps)
│   ├── parser_service.py    ← ParserService: file-type routing (THE entry point)
│   ├── constants.py
│   ├── core/                ← shared engine: key/value parsing, token emission
│   │   ├── key_value_parser.py
│   │   ├── line_parsers/
│   │   ├── token_emitter.py
│   │   └── value_emitters.py
│   ├── basic/               ← generic .zolo features (JSON/YAML replacement)
│   │   ├── block_tracker.py, type_hints.py, validators.py
│   │   ├── value_processors.py, comment_processors.py
│   │   ├── escape_processors.py, multiline_collectors/
│   │   ├── serializer.py    ← dumps() implementation
│   │   └── error_formatter.py
│   └── zvaf/                ← zOS extensions (zUI/zEnv/zSpark/…)
│       ├── zvaf_parser.py
│       ├── file_type_detector.py   ← FileType enum + filename patterns
│       ├── key_detector.py         ← context-aware key classification
│       ├── block_manager.py        ← special blocks (zGate, zMeta, ZNAVBAR, …)
│       ├── modifier_handler.py     ← ^ ~ ! * key modifiers
│       ├── ui_shortcuts.py, key_value_wrapper.py
│       ├── multiline_detection.py
│       └── value_validators.py (+ callback)
│
├── providers/               ← LSP feature logic
│   ├── hover/, completion/, diagnostics/
│   ├── basic/               ← generic-file completions
│   ├── zvaf/                ← zOS-file completions
│   └── shared/
│       ├── documentation_registry.py  ← SSOT for hover/completion docs
│       ├── key_classifications.py
│       └── value_validators.py
│
├── server/
│   ├── lsp_server.py        ← pygls server; wraps ParserService (no parse logic)
│   ├── semantic_tokenizer.py← LSP semantic-token encoding
│   └── code_actions.py
│
├── token_types.py           ← TokenType enum (the token vocabulary)
├── token_registry.py        ← key-set SSOT (ZGATE_OPTION_KEYS, DISPATCH_KEYS, …)
├── lsp_types.py             ← ParseResult & friends
├── exceptions.py
├── version.py               ← __version__ SSOT
│
├── cli/                     ← `zlsp` command (see CLI_GUIDE)
├── editors/                 ← vim/ vscode/ cursor/ installers (see Editors_GUIDE)
├── themes/                  ← zolo_default.yaml SSOT + vim/vscode generators
├── generators/              ← Prism.js pattern generation (see Prism_GUIDE)
├── generated/               ← packaged Prism bundle (ships in the wheel)
└── assets/                  ← filetype icon
```

## The SSOT Chain

Four registries anchor the single-source-of-truth design:

| SSOT | File | Derives |
|------|------|---------|
| Syntax rules | `parser/` (code itself) | tokens, diagnostics, generated grammars |
| Token vocabulary | `token_types.py` | semantic tokens, theme keys, Prism classes |
| Key sets | `token_registry.py` | key classification, gate knobs, dispatch verbs |
| Docs text | `providers/shared/documentation_registry.py` | hover + completion text |
| Colors | `themes/zolo_default.yaml` | every editor theme + Prism CSS |

Change a rule once; every consumer regenerates from it. There are **no
hand-written grammar files** — Vim syntax, VSCode TextMate grammars, and
Prism patterns are all *generated* from these sources (see
[Philosophy_GUIDE](Philosophy_GUIDE.md) for why).

## Public API

```python
from zlsp.parser import load, loads, dump, dumps    # runtime use
from zlsp.parser import tokenize                     # LSP use

data = loads('key: value')                # → {'key': 'value'}
result = tokenize(content, 'zUI.x.zolo')  # → ParseResult(data, tokens, diagnostics)
```

String-first semantics (the `.zolo` core rule):

```python
loads('name: Zolo')        # → 'Zolo'      (string default)
loads('port: 8080')        # → 8080        (unambiguous number)
loads('port(int): 8080')   # → 8080        (explicit hint)
loads('id(str): 12345')    # → '12345'     (forced string)
```

## LSP Server

`server/lsp_server.py` is a thin pygls wrapper — protocol handling only, zero
parse logic. Advertised features:

- `textDocument/semanticTokens/full` — highlighting
- `textDocument/publishDiagnostics` — live errors/warnings
- `textDocument/hover` — key/type documentation
- `textDocument/completion` — context-aware suggestions
- code actions (`server/code_actions.py`)

Transport is **stdio** (standard for LSP; editors spawn `zolo-lsp` directly).
Go-to-definition, references, rename, and formatting are **not implemented**
(candidates for future versions).

## Contributing Map

| You want to… | Touch |
|---|---|
| New syntax | `parser/core/` or `parser/basic/` |
| New zOS construct | `parser/zvaf/` (+ key sets in `token_registry.py`) |
| New token type | `token_types.py` + `server/semantic_tokenizer.py` + theme YAML |
| New file type | `parser/zvaf/file_type_detector.py` |
| Hover/completion text | `providers/shared/documentation_registry.py` |
| Colors | `themes/zolo_default.yaml` **only** — never a generator |

**Never** duplicate parsing logic in grammar files or the LSP server — the
parser is the only component that understands `.zolo`.

## See Also

- [Grammar_GUIDE](Grammar_GUIDE.md) — file types, special blocks, diagnostics
- [Themes_GUIDE](Themes_GUIDE.md) — the color pipeline
- [Prism_GUIDE](Prism_GUIDE.md) — web highlighting
- [pygls](https://github.com/openlawlibrary/pygls) · [LSP spec](https://microsoft.github.io/language-server-protocol/)
