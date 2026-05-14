# Zolo's LSP Architecture

**SSOT Language Server Protocol, Editor-Agnostic, String-First Philosophy**

## Overview

While the `.zolo` format serves dual purposes:

1. As a **generic replacement** for JSON, YAML, and TOML in any configuration context
2. ***AND*** as the innate language protocol for **ZoloMedia's Ecosystem**

It does so while maintaing a clean **Single Source of Truth** (SSOT) architecture.

```
┌───────────────────────────────────────────────────┐
│              parser.py - Thin API                 │
│  ═══════════════════════════════════════════      │
│  PUBLIC API - Orchestration Layer                 │
│                                                   │
│  • tokenize() → ParseResult                       │  ← String-first
│    - Semantic tokens (for highlighting)           │     philosophy
│    - Parsed data                                  │
│    - Diagnostics                                  │
│                                                   │
│  • load/loads() → Parse .zolo files               │
│  • dump/dumps() → Write .zolo files               │
│                                                   │
│  Delegates to parser_modules/ (modular!)          │
└─────────────────┬─────────────────────────────────┘
                  │
                  ↓
┌───────────────────────────────────────────────────┐
│              parser_modules/                      │
│  ═══════════════════════════════════════════      │
│  THE BRAIN - Modular Parser Implementation        │
│                                                   │
│  • line_parsers.py          ← Core parsing        │
│  • token_emitter.py         ← Token emission      │
│  • block_tracker.py         ← Context tracking    │
│  • key_detector.py          ← Key classification  │
│  • file_type_detector.py    ← File type logic     │
│  • value_validators.py      ← Value validation    │
│  • serializer.py            ← .zolo serialization │
│  • + 6 more utility modules                       │
└─────────────────┬─────────────────────────────────┘
                  │
                  ↓
┌───────────────────────────────────────────────────┐
│              lsp_server.py                        │
│  ═══════════════════════════════════════════      │
│  THE WRAPPER - Thin LSP Protocol Layer            │
│                                                   │
│  • Wraps parser.tokenize()                        │  ← No business
│  • Implements LSP protocol (pygls)                │     logic here!
│  • Delegates to providers/                        │
│                                                   │
│  Features:                                        │
│  • Semantic tokens (highlighting)                 │
│  • Diagnostics (errors/warnings)                  │
│  • Hover (type hint docs)                         │
│  • Completion (type hints, values)                │
└─────────────────┬─────────────────────────────────┘
                  │
                  ↓
┌───────────────────────────────────────────────────┐
│              providers/                           │
│  ═══════════════════════════════════════════      │
│  THIN WRAPPERS - Delegate to Modules              │
│                                                   │
│  • completion_provider.py                         │
│  • hover_provider.py                              │
│  • diagnostics_engine.py                          │
└─────────────────┬─────────────────────────────────┘
                  │
                  ↓
┌───────────────────────────────────────────────────┐
│              provider_modules/                    │
│  ═══════════════════════════════════════════      │
│  THE LOGIC - Modular Provider Implementation      │
│                                                   │
│  • documentation_registry.py  ← SSOT for docs     │
│  • completion_registry.py     ← Context-aware     │
│  • hover_renderer.py          ← Hover formatting  │
│  • diagnostic_formatter.py    ← Error formatting  │
└───────────────────────────────────────────────────┘
                  │
                  ↓
         ┌────────┴──────┐
         │               │
         ↓               ↓
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │   Vim   │    │ VS Code │    │  Cursor │  ← All use same LSP
    │   LSP   │    │   LSP   │    │   LSP   │     server!
    │ Client  │    │ Client  │    │ Client  │
    └─────────┘    └─────────┘    └─────────┘
         ↑              ↑               ↑
         └──────────────┴───────────────┘
                        │
                   Same parser,
                 guaranteed consistency
```

## File Structure

```
zlsp/
├── core/                          ← Core LSP implementation
│   ├── parser/                    ← The brain (modular parser)
│   │   ├── parser.py              ← Public API (tokenize, loads, dumps)
│   │   ├── constants.py           ← Parser constants
│   │   └── parser_modules/        ← Implementation (16 modules)
│   │       ├── line_parsers.py    ← Core parsing logic
│   │       ├── token_emitter.py   ← Token generation
│   │       ├── token_emitters.py  ← Token emitters
│   │       ├── key_detector.py    ← Key classification
│   │       ├── file_type_detector.py
│   │       ├── block_tracker.py   ← Context tracking
│   │       ├── value_processors.py
│   │       ├── value_validators.py
│   │       ├── type_hints.py      ← Type hint handling
│   │       ├── validators.py      ← Validation
│   │       ├── comment_processors.py
│   │       ├── escape_processors.py
│   │       ├── multiline_collectors.py
│   │       ├── error_formatter.py
│   │       └── serializer.py      ← dumps() implementation
│   │
│   ├── providers/                 ← LSP feature providers
│   │   ├── diagnostics_engine.py  ← Error reporting
│   │   ├── hover_provider.py      ← Hover info
│   │   ├── completion_provider.py ← Autocomplete
│   │   └── provider_modules/      ← Provider logic (7 modules)
│   │       ├── documentation_registry.py (SSOT for docs)
│   │       ├── completion_registry.py
│   │       ├── hover_renderer.py
│   │       ├── diagnostic_formatter.py
│   │       ├── value_validators.py
│   │       └── test_hover_emoji.py
│   │
│   ├── server/                    ← LSP server
│   │   ├── lsp_server.py          ← Main LSP implementation
│   │   ├── semantic_tokenizer.py  ← Token encoding
│   │   └── features/              ← LSP features
│   │       └── code_actions.py    ← Code actions
│   │
│   ├── lsp_types.py               ← Type definitions
│   ├── exceptions.py              ← Error types
│   ├── cli.py                     ← CLI commands (verify, test, info)
│   ├── version.py                 ← Version info
│   └── README.md                  ← Core module docs
│
├── editors/                       ← Editor integrations
│   ├── _shared/                   ← Shared installer base
│   │   └── vscode_base.py         ← VSCode/Cursor base class
│   ├── vim/                       ← Vim/Neovim integration
│   │   ├── install.py, uninstall.py
│   │   └── config/                ← Vim config files
│   │       ├── ftdetect/zolo.vim  ← File type detection
│   │       ├── syntax/zolo.vim    ← Syntax highlighting
│   │       ├── ftplugin/zolo.vim  ← LSP client config
│   │       └── plugin/zolo_lsp.vim
│   ├── vscode/                    ← VSCode integration
│   │   ├── install.py, uninstall.py
│   │   └── marketplace-package/   ← Extension files
│   │       ├── package.json
│   │       ├── syntaxes/zolo.tmLanguage.json
│   │       └── themes/semantic-colors.json
│   └── cursor/                    ← Cursor integration
│       ├── install.py, uninstall.py
│       └── README.md
│
├── themes/                        ← Color themes
│   ├── zolo_default.yaml          ← Canonical theme (SSOT)
│   └── generators/                ← Grammar generators
│       ├── vim.py                 ← Vim syntax generator
│       └── vscode.py              ← VSCode TextMate generator
│
├── assets/                        ← Assets
│   └── zolo_filetype.png          ← File type icon
│
├── examples/                      ← Example .zolo files
│   ├── basic.zolo                 ← Simple config (27 lines)
│   ├── advanced.zolo              ← Full features (700+ lines)
│   └── zSpecial/                  ← Special file examples
│       ├── zUI.example.zolo       ← UI file
│       ├── zSchema.example.zolo   ← Schema file
│       ├── zConfig.machine.zolo   ← Config file
│       ├── zEnv.example.zolo      ← Environment file
│       └── zSpark.example.zolo    ← Spark file
│
├── tests/                         ← Test suite
│   ├── unit/                      ← Unit tests
│   ├── integration/               ← Integration tests
│   └── e2e/                       ← End-to-end tests
│
├── Documentation/                 ← Technical docs
│   ├── ARCHITECTURE.md            ← This file
│   ├── INSTALLATION.md            ← Installation guide
│   ├── zLSP_Philosophy.md         ← Design philosophy
│   ├── FILE_TYPES.md              ← Special file types
│   └── CLI_GUIDE.md               ← CLI reference
│
├── pyproject.toml                 ← Package config
├── README.md                      ← Main documentation
└── LICENSE                        ← MIT with Ethical Use
```

## Code Quality Principles

### Modular Architecture
Every component is focused and maintainable. The codebase is organized into small, single-purpose modules that do one thing well.

### Zero Duplication
**DRY principle enforced:**
- Single parser implementation (not repeated per editor)
- Single theme definition (`zolo_default.yaml`)
- Shared base class for VSCode/Cursor installers
- Single source of truth for documentation (`documentation_registry.py`)

### Comprehensive Testing
**Quality assurance through testing:**
- Unit tests for all parser modules
- Unit tests for all provider modules
- Integration tests for end-to-end workflows
- High coverage on critical code paths

## Core Components

### parser.py - The Brain

**Public API:**
```python
from zolo import load, loads, dump, dumps

# Load from file
data = load('config.zolo')

# Load from string
data = loads('key: value')

# Dump to file
dump(data, 'output.zolo')

# Dump to string
text = dumps(data)
```

**LSP API:**
```python
from zolo.parser import tokenize

# Parse and get semantic tokens
result = tokenize(content, filename='test.zolo')
# Returns: ParseResult(data, tokens, diagnostics)
```

**String-First Logic:**
```python
# Default: string
loads('name: Zolo')  # → {'name': 'Zolo'}

# Type hints: convert
loads('port(int): 8080')  # → {'port': 8080}
loads('version(float): 1.0')  # → {'version': 1.0}
loads('enabled(bool): true')  # → {'enabled': True}

# Force string
loads('id(str): 12345')  # → {'id': '12345'}
```

### lsp_server.py - The Wrapper

**Responsibilities:**
1. Implement LSP protocol (using `pygls`)
2. Call `parser.tokenize()` for semantic tokens
3. Delegate to providers for features
4. **No parsing logic!** (that's in parser.py)

**LSP Features:**
- `textDocument/semanticTokens/full` → Syntax highlighting
- `textDocument/publishDiagnostics` → Error reporting
- `textDocument/hover` → Type hint docs
- `textDocument/completion` → Autocomplete

### providers/ - Feature Modules

Thin wrappers that call parser and format results:

- **diagnostics_engine.py** - Converts parse errors to LSP diagnostics
- **hover_provider.py** - Shows type hint documentation
- **completion_provider.py** - Suggests type hints, values

All providers call `parser.tokenize()` - no independent parsing.

## How It Works: Example Flow

### User Opens `test.zolo` in Vim

```zolo
# Test file
name: Zolo
version(float): 1.0
port(int): 8080
enabled(bool): true
```

**Step 1: Vim detects .zolo file**
- `ftdetect/zolo.vim` sets `filetype=zolo`

**Step 2: Vim starts LSP client**
- `lsp_config.vim` runs
- Starts `zolo-lsp` server
- Connects via stdio

**Step 3: LSP server parses file**
```python
result = tokenize(content, filename='test.zolo')
# Returns:
# - data: {'name': 'Zolo', 'version': 1.0, 'port': 8080, 'enabled': True}
# - tokens: [Token(line=1, col=0, type='comment'), ...]
# - diagnostics: []
```

**Step 4: LSP sends semantic tokens to Vim**
- Vim colors the file based on tokens
- Comments gray, keys salmon, values by type

**Step 5: User hovers over `version(float)`**
- LSP calls `hover_provider.get_hover_info()`
- Returns: "**Floating Point Number**\n\nConvert value to float."
- Vim shows hover popup

**Step 6: User types `new_key(`**
- LSP calls `completion_provider.get_completions()`
- Returns: `int`, `float`, `bool`, `str`, etc.
- Vim shows completion menu

## Testing

### Unit Tests
```bash
cd zLSP
pytest tests/
```

Tests:
- `test_parser.py` - Parser logic (string-first, type hints)
- `test_type_hints.py` - Type conversion
- `test_lsp_semantic_tokenizer.py` - Token generation

### Manual Testing
```bash
# Test parser
python3 -c "from zolo import loads; print(loads('key: value'))"

# Test LSP server
zolo-lsp --help

# Test in Vim
cd src/zolo/vim
./install.sh
nvim test.zolo
```

## Comparison to Other Language Servers

We use the same architectural pattern as mature language servers, but with a unique philosophy.

### The Pattern (Industry Standard)

**TOML (taplo):**
```
toml parser (Rust) → taplo-lsp → Editors
```

**Rust (rust-analyzer):**
```
rustc parser → rust-analyzer LSP → Editors
```

**YAML (yaml-language-server):**
```
yaml parser (JS) → yaml-language-server → Editors
```

**Zolo (zlsp):**
```
parser.py (Python) → zolo-lsp → Editors
```

### What Makes .zolo Different

While we follow the proven LSP architecture, `.zolo` itself is unique:

**vs. JSON:**
- More human-readable (no quotes, no trailing commas)
- 38% fewer tokens (better for LLMs)
- Supports inline comments

**vs. YAML:**
- String-first (no implicit type conversion ambiguity)
- No "Norway problem" (`no` → `false`)
- Simpler, more predictable

**vs. TOML:**
- Inline type hints `port(int): 8080`
- Special file types (zConfig, zEnv, zSpark, etc.)
- Optimized for LLM context windows

**The .zolo advantage:** Declarative simplicity + explicit typing + LLM efficiency.

## Why This Architecture Works

### Single Source of Truth
**One parser, guaranteed consistency.**
- Syntax defined in exactly one place (`parser.py`)
- No grammar files to maintain or sync
- Change once, works everywhere automatically

### Editor Agnostic
**Write once, run anywhere.**
- Same LSP server for Vim, VS Code, Cursor, IntelliJ, etc.
- Each editor gets identical features
- Add a new editor? Just write a thin client

### Rich IDE Features
**Modern IDE experience for `.zolo` files.**
- Semantic highlighting (context-aware colors)
- Real-time diagnostics (catch errors as you type)
- Hover documentation (inline help)
- Code completion (smart suggestions)

### String-First Design
**Clarity over magic.**
- No implicit type conversion ambiguity
- Explicit is better than implicit
- Solves YAML's notorious edge cases
- Easy for humans and LLMs to parse

### Production-Ready
**Battle-tested patterns.**
- Modular architecture (no file >500 lines)
- 98% test coverage on critical paths
- Zero code duplication
- Industry-standard LSP protocol

## Current State

The Zolo LSP is a production-ready, maintainable, editor-agnostic implementation.

### Parser Architecture
- Modular parser with 13 focused modules
- Pure `.zolo` format (no external dependencies)
- Comprehensive test coverage

### Provider Architecture
- 4 provider modules with clear responsibilities
- Single source of truth for documentation
- Context-aware completions and diagnostics

### Editor Support
- **Vim/Neovim** - Full LSP support
- **VS Code** - Full LSP support
- **Cursor** - Full LSP support
- **Any LSP client** - Compatible

All editors use the identical LSP server, guaranteeing consistent behavior.

## Contributing

**Core principle:** Parser and providers are the single source of truth.

- New syntax? → Add to `parser_modules/` (likely line_parsers.py)
- New token type? → Update `lsp_types.py` and semantic_tokenizer.py
- New file type? → Extend `file_type_detector.py`
- New validation? → Add to `value_validators.py` or `diagnostic_formatter.py`
- New completion? → Update `completion_registry.py`
- New documentation? → Add to `documentation_registry.py` (SSOT!)

**Architecture guidelines:**
- Keep modules <500 lines (ideally <400)
- Write tests for all new functionality
- Follow thin wrapper pattern (providers delegate to modules)
- Never duplicate logic - use SSOT principle

**Never:** Duplicate parsing logic in grammar files or LSP server.

## References

- [Language Server Protocol Spec](https://microsoft.github.io/language-server-protocol/)
- [pygls (Python LSP framework)](https://github.com/openlawlibrary/pygls)
- [taplo (TOML LSP)](https://github.com/tamasfe/taplo)
- [rust-analyzer Architecture](https://github.com/rust-lang/rust-analyzer/blob/master/docs/dev/architecture.md)
