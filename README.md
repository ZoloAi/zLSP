# zLSP - Language Server Protocol for .zolo Files

**Language Server Protocol implementation for `.zolo` declarative configuration files**

## About
**zLSP** is the official Language Server Protocol for `.zolo`.

`.zolo` is a modern, string-first declarative format designed to replace JSON, YAML, and TOML. **optimized for developer experience, runtime efficiency, and LLM workflows**.

**zLSP** brings full IDE intelligence to `.zolo` files, including semantic highlighting, diagnostics, hover information, and code completion.

The `.zolo` format serves dual purposes:
1. As a **generic replacement** for JSON, YAML, and TOML in any configuration context
2. ***AND*** as the innate language protocol for **ZoloMedia's zEcosystem**.

Browse to [**basic.zolo**](examples/basic.zolo) or [**advanced.zolo**](examples/advanced.zolo) for syntax and structure examples.

> **Note:** The Zolo ecosystem is format-agnostic. While `.zolo` is its native language, zOS also supports JSON, YAML, and other declarative dictionary-based formats.  
> See the [**zOS README**](../zOS/README.md) for details.

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

## Installation

In Terminal run the following command:

```bash
pip install zlsp
```

Then install for your editor:

```bash
zlsp-install-all      # Install for all editors + generate Prism.js
zlsp-install-vim      # Automated Vim/Neovim integration
zlsp-install-vscode   # Automated VSCode integration
zlsp-install-cursor   # Automated Cursor integration
zlsp-generate-prism   # Generate web syntax highlighting only (Prism.js)
```

## Verify Installation

After installation, verify everything is working:

```bash
zlsp verify              # Quick health check
zlsp verify --verbose    # Detailed check with all components
```

This runs 5 essential checks:
- [ok] Python version compatibility
- [ok] Core dependencies (pygls, lsprotocol)
- [ok] Parser functionality
- [ok] LSP server availability
- [ok] Semantic tokenizer

If anything fails, you'll get clear error messages with suggested fixes. Exit code 0 means success, 1 means issues found.

> For installation troubleshoots see: [**INSTALLATION.md**](Documentation/INSTALLATION.md)

## Features

- **String-First Philosophy** - Values are strings by default with explicit type hints as needed
- **Optimized Parser Architecture** - Early file type detection with dual-path routing (Basic/zVaF)
- **Pure LSP Architecture** - Parser is the source of truth, no grammar files
- **Editor Agnostic** - Works with Vim, VSCode, Cursor, and any LSP-compatible editor
- **Semantic Highlighting** - Context-aware syntax coloring
- **Real-Time Diagnostics** - Syntax errors and type validation
- **Code Completion** - Two-tier provider system (basic vs zVAF) with theme-driven completions
  - **58% faster** for generic .zolo files (lightweight BasicCompletionProvider)
  - **Full-featured** for zVAF files (ZVAFCompletionProvider with theme integration)
  - **Zero duplication** - All completions from SSOT (documentation registry, theme YAML)
- **Hover Information** - Inline documentation and type information

> **Design Philosophy:** See [**zLSP_Philosophy.md**](Documentation/zLSP_Philosophy.md) for the principles behind string-first syntax.

## Parser Architecture

zLSP uses an **optimized dual-path parser** with early file type detection for maximum performance:

### File Types & Routing

**Basic .zolo files** (generic config):
- Route: `config.zolo` → **Basic Parser** (Core + Basic features only)
- Features: Indentation, type hints, arrays, dash lists, multiline strings
- Performance: ~20% faster (no zVaF overhead)

**zVaF .zolo files** (zOS special types):
- Route: `zUI.*.zolo`, `zEnv.*.zolo`, `zSpark.*.zolo` → **zVaF Parser** (Core + Basic + zVaF)
- Features: All Basic features PLUS modifiers (`^`, `~`, `!`, `*`), auto-multiline, UI shorthands
- Detection: Automatic via filename pattern

### Performance Benefits

**Early Detection** - File type detected at server entry point (before any parsing):
```
LSP Request → FileTypeDetector → Route to appropriate parser
                                  ├─ Basic: No zVaF code touched
                                  └─ zVaF: Full extensions enabled
```

**Zero Overhead** - Basic files never load or execute zVaF code, resulting in faster parsing and lower memory usage.

> See [**PARSER_ROUTING_ARCHITECTURE.md**](PARSER_ROUTING_ARCHITECTURE.md) for complete architectural details.

## Why .zolo?

Configuration files consume significant space in LLM contexts.  
When you're working with AI assistants or processing configs at scale, every token counts.  
**The `.zolo` format is designed with this reality in mind.**

**Token Comparison** (measured from [**advanced.zolo**](examples/advanced.zolo) - 400 lines of real-world config):

| Format | Tokens | vs JSON | Why? |
|--------|--------|---------|------|
| **JSON** (baseline) | 7,358 | — | Industry standard, but verbose with `{}`, `[]`, `""` everywhere |
| YAML | 4,905 | 33% smaller | Clean syntax, but ambiguous (`yes` = `true`, bare strings behave unpredictably) |
| TOML | 5,813 | 21% smaller | Explicit types, but repetitive `[section.headers]` for nesting |
| **`.zolo`** | **4,542** | **38% smaller** | **String-first, explicit types, minimal syntax** |

**What does 38% token reduction mean?**

In practical terms, a typical application configuration that consumes **7,358 tokens in JSON** requires only **4,542 tokens in .zolo**.  
**That's 2,816 tokens saved** - enough space for several additional prompts or responses in an LLM conversation.

**Scale Amplifies Savings** - The more files you process, the more tokens you save (Impact Multiplier shows the growing benefit):

| Scale | JSON Tokens | .zolo Tokens | Tokens Saved | Impact Multiplier | Equivalent To |
|-------|-------------|--------------|--------------|-------------------|---------------|
| 1 file | 7,358 | 4,542 | 2,816 | 1x | ~4 LLM prompts |
| 10 files | 73,580 | 45,420 | 28,160 | 10x | ~40 prompts |
| 100 files | 735,800 | 454,200 | 281,600 | 100x | ~400 prompts |
| 1,000 files | 7,358,000 | 4,542,000 | 2,816,000 | 1,000x | ~4,000 prompts |

**What this means for you:**
- **Save 38% on AI API bills** - Every token you don't send is money saved
- **Fit more in AI conversations** - More room for your actual data and prompts
- **Faster load times** - Smaller files process quicker
- **Easier to read** - Less clutter, more clarity

**Why not just use YAML?**

YAML achieves similar token efficiency (33% reduction) but introduces ambiguity that causes production issues:
- `yes`, `no`, `on`, `off` auto-convert to booleans
- Bare strings like `true` or `false` become booleans unexpectedly
- The infamous "Norway problem" where country code `no` becomes `false`
- Implicit type conversions lead to bugs

>**Suggested reading:** [The yaml document from hell](https://ruudvanasseldonk.com/2023/01/11/the-yaml-document-from-hell) - A comprehensive breakdown of YAML's footguns and unexpected behaviors.

`.zolo` takes a different approach: **string-first with explicit types**. Only `true` and `false` are booleans, everything else is a string. This eliminates ambiguity while maintaining readability and token efficiency - a practical format for both humans and machines.

## String-First Philosophy

zLSP's core design: **values are strings by default**, with explicit type hints for conversion.

```zolo
# Strings (default)
name: Zolo
description: A declarative config format

# Explicit type conversion
version(float): 1.0
port(int): 8080
enabled(bool): true

# Force string (even if looks like number)
id(str): 12345

# Null values
empty(null):
```

**Why String-First?**
- Strings are the most common value type in declarative files, especially in the LLM era
- Optimized for the actual use case (text, paths, commands, descriptions)
- Side benefit: eliminates ambiguity (no `yes` = `true` confusion)
- Explicit type hints when you need other types


## Architecture

zLSP follows modern Language Server Protocol best practices with a modular, layered architecture:

```
parser.py (Public API)
    ↓
┌─────────────────────────────────────┐
│  Parser Modules (3 layers)          │
│  ├── basic/     (format-agnostic)   │
│  ├── core/      (orchestration)     │
│  └── zvaf/      (domain-specific)   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Token System (centralized)         │
│  ├── token_types.py   (enum)        │
│  └── token_registry.py (mappings)   │
└─────────────────────────────────────┘
    ↓
lsp_server.py (LSP Protocol)
    ↓
┌─────────────────────────────────────┐
│  Providers (2-tier architecture)    │
│  ├── completion/                    │
│  │   ├── completion_router.py      │
│  │   ├── basic/ → lightweight      │
│  │   └── zvaf/  → full-featured    │
│  ├── diagnostics/                   │
│  ├── hover/                         │
│  └── shared/    (SSOT modules)      │
│      ├── documentation_registry.py  │
│      ├── key_classifications.py    │
│      └── value_validators.py       │
└─────────────────────────────────────┘
    ↓
Editor Clients (vim-lsp, VSCode LSP, Cursor)
```

**Key Principles:**
- **Single Source of Truth (SSOT)** - Each concern has one authoritative source:
  - **Parser Layer:**
    - Token types → `token_types.py` (enum definitions)
    - Token mappings → `token_registry.py` (LSP indices, key sets, block constants)
    - UI element definitions → `UI_ELEMENT_MAPPING` (22 elements, 1 location)
    - Special blocks → `SPECIAL_BLOCK_MAPPING` (zRBAC, zMeta, ZNAVBAR, zMachine, zSpark)
    - Type hint parsing → `basic/type_hints.py` (`extract_type_hint()`)
    - Root key validation → `basic/validators.py` (`validate_root_key()`)
    - Multiline detection → `key_detector.should_enable_auto_multiline()`
    - Modifier handling → `modifier_handler.py` (parsing + token emission)
  - **Provider Layer (Phase 1-3):**
    - Type hints & docs → `providers/shared/documentation_registry.py`
    - Block keys & UI elements → `providers/shared/key_classifications.py` (40 block keys, 17 UI elements)
    - Key completions → `themes/zolo_default.yaml` (context-aware, per file type)
    - Value completions → `themes/zolo_default.yaml` (per-key definitions)
    - Completion routing → `providers/completion/completion_router.py` (basic vs zVAF)
- **DRY Architecture** - No duplication of parsing logic:
  - UI elements: 80+ lines of elif chains → 40 lines of mapping lookups
  - Block entry: Consolidated `enter_block_for_key()` + `enter_nested_block_for_key()` (90% overlap eliminated)
  - Type hints: 9+ scattered `TYPE_HINT_PATTERN.match()` calls → 1 centralized helper
  - Root validation: Duplicated 18-line blocks → single reusable function
  - Modifier emission: Single `emit_key_with_modifiers()` function (SSOT)
- **Data-Driven Design** - Behavior defined by mappings, not code:
  - Adding UI elements: Edit 1 mapping dictionary (previously 5+ files)
  - Block types auto-derived from mappings
  - Shorthand sets auto-generated from mapping properties
- **Modular Design** - Clean separation between generic and domain-specific:
  - `basic/` - Format-agnostic primitives (YAML/JSON features)
  - `core/` - Orchestration layer (format-neutral)
  - `zvaf/` - Domain-specific zOS features (UI elements, multiline detection, file types)
- **Thin LSP Wrapper** - Parser is source of truth, LSP server delegates
- **Feature-Based Providers** - Completion, diagnostics, hover organized by feature
- **Editor-Agnostic** - Pure LSP protocol, works with any LSP client

### Modifier Architecture (SSOT/DRY Example)

The modifier system demonstrates SSOT and DRY principles:

```
modifier_handler.py (SSOT: Parsing Logic)
    ↓ split_modifiers('^logout*') → ('^', 'logout', '*')
    ↓
modifier_parser.py (SSOT: Token Emission)
    ↓ emit_key_with_modifiers() → emits tokens for ^, logout, *
    ↓
key_value_wrapper.py (zVaF Wrapper)
    ↓ Uses both SSOT modules for zVaF-specific key parsing
```

**Key Files:**
- `modifier_handler.py` - SSOT for modifier character sets (`^~*!`) and splitting logic
- `modifier_parser.py` - SSOT for emitting semantic tokens for modifiers
- `key_value_wrapper.py` - zVaF-specific wrapper that delegates to SSOT modules

**Why This Design:**
- Modifier parsing logic defined once (`modifier_handler.py`)
- Token emission logic defined once (`modifier_parser.py`)
- Wrapper functions delegate to SSOT (no duplication)
- Clear separation: parsing vs emission vs orchestration

### Completion Provider Architecture (Phase 1-3)

The completion system uses a **two-tier provider architecture** with intelligent routing:

```
User Types in .zolo File
    ↓
get_completions(content, line, char, filename)
    ↓
CompletionRouter.route()
    ↓
detect_file_type(filename)
    ↓
┌─────────────────────┬──────────────────────┐
│ FileType.GENERIC    │ FileType.ZSPARK      │
│                     │ FileType.ZUI         │
│                     │ FileType.ZSCHEMA     │
└─────────┬───────────┴───────────┬──────────┘
          │                       │
          ▼                       ▼
┌──────────────────┐    ┌─────────────────────┐
│ Basic Provider   │    │ zVAF Provider       │
│ (lightweight)    │    │ (full-featured)     │
├──────────────────┤    ├─────────────────────┤
│ ✅ Type hints    │    │ ✅ Type hints       │
│ ✅ Common values │    │ ✅ Common values    │
│ ❌ File types    │    │ ✅ File-type keys   │
│ ❌ Themes        │    │ ✅ Value completions│
│                  │    │ ✅ Theme loading    │
│ 🚀 ~50ms         │    │ 🎯 ~150ms (cached)  │
└──────────────────┘    └─────────────────────┘
```

**SSOT Sources:**
1. `providers/shared/documentation_registry.py` - Type hints & common values (12 hints, 2 values)
2. `providers/shared/key_classifications.py` - Block keys & UI elements (40 keys, 17 elements)
3. `themes/zolo_default.yaml` - Key completions (per file type, context-aware)
4. `themes/zolo_default.yaml` - Value completions (per key, e.g., zState → [Production, Development])

**Performance:**
- Generic .zolo files: **58% faster** (no theme loading, no file-type overhead)
- zVAF files: Same speed, cleaner architecture

**Benefits:**
- Zero duplication (all data from SSOT)
- Independent evolution (basic stabilizes, zVAF evolves)
- Easy maintenance (change once, affects all)
- User customization (theme-based completions)

> See [COMPLETION_ARCHITECTURE.md](COMPLETION_ARCHITECTURE.md) and [PHASE3_ARCHITECTURE.md](PHASE3_ARCHITECTURE.md) for complete details.

### Parser Separation (Basic/zVaF Example)

The parser demonstrates clean separation of basic JSON/YAML features from zVaF-specific extensions:

**Line Parsers:**
```
core/line_parsers/standard_parser.py (Basic Module)
    ├── parse_lines()                # Basic: JSON/YAML parser (extensible via callbacks)
    │   ↓ Optional: auto_multiline_checker param (for domain-specific multiline rules)
    │   ↓ Optional: dict_builder param (for domain-specific dict building)
    └── Uses callbacks to extend behavior without modifying core logic

zvaf/zvaf_parser.py (zVaF Extension - Domain-Specific)
    └── parse_lines_zvaf()           # zVaF: Wrapper with UI extensions
        ↓ Delegates to parse_lines() with zVaF callbacks:
        ↓   - check_auto_multiline_for_key() (auto-multiline for zText, zMD)
        ↓   - build_nested_dict_zvaf() (UI shorthand support)
```

**Dictionary Builder:**
```
core/line_parsers/dict_builder.py (Basic Module with Extension Points)
    ├── build_nested_dict()          # Basic: JSON/YAML mode (strict duplicate checking)
    │   ↓ Uses duplicate_key_handler callback for extensibility
    └── build_nested_dict_zvaf()     # zVaF: Wrapper with UI shorthand support
        ↓ Delegates to build_nested_dict() with zVaF handler
        ↓
    _zvaf_duplicate_key_handler()    # zVaF: UI element duplicate handling
        ↓ Uses zvaf/ui_shortcuts.py for UI detection
```

**Key Features:**
- **Basic Mode**: Generic JSON/YAML parsing with strict rules (no domain-specific behavior)
- **zVaF Mode**: UI element extensions (auto-multiline, repeatable UI shorthands like zText, zButton)
- **Callback Pattern**: Extension points enable domain-specific behavior without core logic changes

**Why This Design:**
- Core parser is format-agnostic (works for any JSON/YAML-like format)
- zVaF extensions injected via callbacks (no modification of core logic)
- Clean separation: basic features vs domain-specific features
- Testable in isolation: basic mode can be tested without zVaF dependencies
- Backwards compatible: Default behavior uses zVaF extensions

## Usage as Parser

> **⚠️ Import Warning:** Use `from zlsp import parser` or `from zlsp.parser import ...`. Do NOT use `import zolo` - that's a different public package on PyPI unrelated to this project.

```python
from zlsp.parser import load, loads, dump, dumps

# Load from file
data = load('config.zolo')

# Load from string
data = loads('''
name: Zolo
version(float): 1.0
enabled(bool): true
''')
# → {'name': 'Zolo', 'version': 1.0, 'enabled': True}

# Write to file
dump(data, 'output.zolo')

# Write to string
text = dumps(data)
```

### Advanced: Token Types and Registry

For LSP development or custom tooling, you can access the centralized token system:

```python
from zlsp.token_types import TokenType
from zlsp.token_registry import (
    TOKEN_TYPE_MAP,              # Enum → LSP index mapping
    TOKEN_TYPES_LEGEND,          # Ordered list for LSP
    
    # Key sets for detection
    ZOS_DATA_KEYS,
    UI_ELEMENT_KEYS,
    UI_ELEMENT_PROPERTY_KEYS,
    
    # Block type constants (centralized)
    BLOCK_ZIMAGE,
    BLOCK_ZTEXT,
    UI_ELEMENT_BLOCK_TYPES,      # List of all UI element blocks
    
    # NEW: Data-driven mappings (SSOT)
    UI_ELEMENT_MAPPING,          # Maps UI elements → block types, properties
    SPECIAL_BLOCK_MAPPING,       # Maps special blocks (zRBAC, zMeta, etc.)
    UI_ELEMENT_SHORTHAND_KEYS,   # Set of repeatable UI elements
)

# All token types (43 total)
print(f"Token types: {len(TOKEN_TYPES_LEGEND)}")

# Get LSP index for a token type
index = TOKEN_TYPE_MAP[TokenType.COMMENT]  # → 0

# Check if a key is a UI element (using centralized mapping)
if 'zImage' in UI_ELEMENT_MAPPING:
    block_info = UI_ELEMENT_MAPPING['zImage']
    print(f"Block: {block_info['block_type']}")        # → BLOCK_ZIMAGE
    print(f"Requires zUI: {block_info['requires_zui']}")  # → True
    print(f"Is shorthand: {block_info['is_shorthand']}")  # → True

# Check if element can repeat in sequence
if 'zText' in UI_ELEMENT_SHORTHAND_KEYS:
    print("zText can appear multiple times")

# Special blocks (zRBAC, zMeta, ZNAVBAR, zMachine, zSpark)
if 'zRBAC' in SPECIAL_BLOCK_MAPPING:
    block_info = SPECIAL_BLOCK_MAPPING['zRBAC']
    print(f"Method: {block_info['method']}")  # → 'enter_block'
```

The token registry serves as the single source of truth, providing:
- **Token type mappings** - Auto-generated enum → LSP index mappings
- **Key sets** - Centralized detection sets (ZOS_DATA_KEYS, UI_ELEMENT_KEYS, etc.)
- **Block constants** - Standardized block type identifiers
- **NEW: Data-driven mappings** - UI_ELEMENT_MAPPING and SPECIAL_BLOCK_MAPPING eliminate hardcoded elif chains
- **Derived sets** - Auto-generated convenience sets (UI_ELEMENT_SHORTHAND_KEYS)

**Adding a new UI element now requires editing only ONE location:**
```python
# In token_registry.py
UI_ELEMENT_MAPPING = {
    'zNewElement': {
        'block_type': BLOCK_ZNEW,
        'block_name': 'znew',
        'requires_zui': True,
        'is_shorthand': True,
    },
    # ... existing elements
}
```

All mappings are auto-generated and validated at import time, eliminating manual synchronization across 5+ files.

## zLSP Advanced Features

zLSP server provides all the expected industry-grade features:

### Semantic Highlighting
- Keys, values, and comments colored by parser
- Context-aware for special file types (zConfig, zEnv, zSpark)
- Type hints highlighted

### Diagnostics
- Syntax errors (duplicate keys, invalid format)
- Type mismatches (e.g., `port(int): abc`)
- Real-time error reporting

### Hover Information
- Type hint documentation
- Value type detection
- Key descriptions

### Code Completion (Phase 1-3 Enhanced)

**Two-Tier Provider Architecture:**
- **Generic .zolo files** → BasicCompletionProvider (58% faster)
  - Type hints: `(int)`, `(float)`, `(bool)`, `(str)`, `(list)`, `(dict)`, `(null)`, `(raw)`, `(date)`, `(time)`, `(url)`, `(path)`
  - Common values: `true`, `false`, `null`
  - No file-type overhead
  
- **zVAF files** → ZVAFCompletionProvider (full features)
  - All basic completions
  - File-type-specific keys from theme YAML (zSpark, zUI, zSchema, zConfig, zEnv)
  - Value completions per key (e.g., `zState: █` → Production, Development)
  - UI element completions (zImage, zText, zH1-zH6, etc.)
  - Block key detection (skip value completions for block keys)
  - Parent key context (nested completions)

**SSOT Architecture:**
- Type hints & docs → `documentation_registry.py`
- Block keys & UI elements → `key_classifications.py` (40 block keys, 17 UI elements)
- File-type keys → `themes/zolo_default.yaml`
- File-type + key values → `themes/zolo_default.yaml`
- Routing logic → `completion_router.py`

> See [COMPLETION_ARCHITECTURE.md](COMPLETION_ARCHITECTURE.md) and [PHASE3_ARCHITECTURE.md](PHASE3_ARCHITECTURE.md) for complete details.

## Project Structure

```
zlsp/
├── zlsp/                      # Core LSP implementation
│   ├── lsp_types.py           # Core LSP types (Position, Range, SemanticToken)
│   ├── token_types.py         # TokenType enum (single source of truth)
│   ├── token_registry.py      # Token mappings + key sets + block constants (SSOT)
│   ├── parser/                # Parser (single source of truth)
│   │   ├── parser.py          # Public API (load, loads, dump, dumps, tokenize)
│   │   ├── constants.py       # Parser constants
│   │   ├── basic/             # Format-agnostic parsing primitives
│   │   │   ├── block_tracker.py
│   │   │   ├── type_hints.py
│   │   │   ├── serializer.py
│   │   │   ├── validators.py
│   │   │   ├── value_processors.py
│   │   │   ├── comment_processors.py
│   │   │   ├── escape_processors.py
│   │   │   ├── multiline_collectors/  # Multiline value collectors (modular)
│   │   │   │   ├── str_hint.py
│   │   │   │   ├── dash_list.py
│   │   │   │   ├── bracket_array.py
│   │   │   │   ├── pipe.py
│   │   │   │   └── triple_quote.py
│   │   │   └── error_formatter.py
│   │   ├── core/              # Core integration layer
│   │   │   ├── token_emitter.py
│   │   │   ├── value_emitters.py
│   │   │   ├── key_value_parser.py
│   │   │   └── line_parsers/  # Line parsing logic
│   │   │       ├── dict_builder.py              # Dict building (basic + zvaf modes)
│   │   │       ├── standard_parser.py           # Runtime parser
│   │   │       ├── tokenizing_parser.py         # LSP parser with tokens
│   │   │       ├── multiline_token_handlers.py  # Multiline token emission (consolidated)
│   │   │       ├── indentation.py               # Indentation validation
│   │   │       └── root_parser.py               # Root-level parsing
│   │   └── zvaf/              # zVaF-specific domain knowledge (zOS features)
│   │       ├── file_type_detector.py    # Early file type detection
│   │       ├── key_detector.py          # SSOT: Key type detection (uses token_registry)
│   │       ├── value_validators.py      # zVaF value validation
│   │       ├── ui_shortcuts.py          # UI shorthand detection (uses UI_ELEMENT_SHORTHAND_KEYS)
│   │       ├── multiline_detection.py   # Auto-multiline detection (delegates to key_detector)
│   │       ├── zvaf_parser.py           # zVaF parser wrapper (delegates to standard_parser)
│   │       ├── modifier_handler.py      # SSOT: Modifier parsing + token emission (^~*!)
│   │       ├── key_value_wrapper.py     # zVaF key parsing wrapper (uses type_hints, validators)
│   │       └── block_manager.py         # SSOT: Block entry logic (uses mappings)
│   ├── providers/             # LSP feature providers (Phase 1-3 enhanced)
│   │   ├── basic/             # Basic completions (generic .zolo)
│   │   │   └── basic_completion_provider.py  # Lightweight, fast
│   │   ├── zvaf/              # zVAF completions (zSpark, zUI, zSchema, etc.)
│   │   │   └── zvaf_completion_provider.py   # Full-featured, theme-driven
│   │   ├── completion/        # Completion system
│   │   │   ├── completion_provider.py   # Public API (routes)
│   │   │   ├── completion_router.py     # Routing logic (basic vs zVAF)
│   │   │   └── registry.py              # Legacy (compatibility)
│   │   ├── diagnostics/       # Error reporting
│   │   │   ├── diagnostic_provider.py
│   │   │   └── formatter.py
│   │   ├── hover/             # Hover information
│   │   │   ├── hover_provider.py
│   │   │   └── renderer.py
│   │   └── shared/            # Shared provider utilities (SSOT)
│   │       ├── documentation_registry.py     # Type hints & docs (SSOT)
│   │       ├── key_classifications.py        # Block keys & UI elements (SSOT)
│   │       └── value_validators.py           # Value validation
│   ├── server/                # LSP server implementation
│   │   ├── lsp_server.py      # Main LSP server
│   │   ├── semantic_tokenizer.py
│   │   └── code_actions.py
│   ├── editors/               # Editor integrations
│   │   ├── _shared/           # Shared installer base
│   │   ├── vim/               # Vim/Neovim integration
│   │   ├── vscode/            # VSCode integration
│   │   └── cursor/            # Cursor IDE integration
│   ├── themes/                # Color themes
│   │   ├── zolo_default.yaml  # Canonical theme
│   │   └── generators/        # Editor-specific generators
│   └── cli/                   # CLI commands
├── examples/                  # Example .zolo files
├── Documentation/             # Full documentation
├── REFACTORING_SUMMARY.md     # Token system refactoring details
└── REFACTORING_DIAGRAM.md     # Visual before/after comparison
```

## Documentation

### Getting Started
- [INSTALLATION.md](Documentation/INSTALLATION.md) - Detailed installation guide
- [basic.zolo](examples/basic.zolo) - Simple syntax examples
- [advanced.zolo](examples/advanced.zolo) - Real-world configuration example

### Core Documentation
- [ARCHITECTURE.md](Documentation/ARCHITECTURE.md) - Design and architecture
- [PARSER_ROUTING_ARCHITECTURE.md](PARSER_ROUTING_ARCHITECTURE.md) - Parser routing & performance
- [COMPLETION_ARCHITECTURE.md](COMPLETION_ARCHITECTURE.md) - Completion system SSOT architecture (Phases 1-2)
- [PHASE3_ARCHITECTURE.md](PHASE3_ARCHITECTURE.md) - Provider separation: Basic vs zVAF (Phase 3)
- [FILE_TYPES.md](Documentation/FILE_TYPES.md) - File type detection and LSP features
- [CLI_GUIDE.md](Documentation/CLI_GUIDE.md) - Complete CLI reference
- [COLOR_LEDGER.md](Documentation/COLOR_LEDGER.md) - Complete token color reference (all file types)

### Editor Integration
- [editors/vim/README.md](editors/vim/README.md) - Vim/Neovim setup
- [editors/vscode/README.md](editors/vscode/README.md) - VSCode setup
- [editors/cursor/README.md](editors/cursor/README.md) - Cursor IDE setup


## Development

```bash
# Clone repository
git clone https://github.com/ZoloAi/ZoloMedia.git
cd ZoloMedia/zlsp

# Install in editable mode
pip install -e .

# Install for your editor
zlsp-install-vim  # or zlsp-install-vscode

# Run tests
pytest tests/

# Test parser (automatic routing based on filename)
python3 -c "from zlsp.parser import loads; print(loads('key: value', filename='config.zolo'))"

# Start LSP server
zolo-lsp
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov-report=html

# Test specific module
pytest tests/unit/test_parser.py
```

## Contributing

**Core Principles:** SSOT (Single Source of Truth) and DRY (Don't Repeat Yourself)

### Parser Layer
- **New syntax?** → Update parser (single source of truth)
- **New highlighting?** → Update tokenizer (uses parser output)
- **New UI element?** → Add to `UI_ELEMENT_MAPPING` in `token_registry.py` (ONE location)
- **New special block?** → Add to `SPECIAL_BLOCK_MAPPING` in `token_registry.py`
- **Type hint logic?** → Update `basic/type_hints.py` (`extract_type_hint()`)
- **Root validation?** → Update `basic/validators.py` (`validate_root_key()`)
- **Multiline detection?** → Update `key_detector.should_enable_auto_multiline()`
- **Modifier logic?** → Update `modifier_handler.py` (SSOT for modifier parsing + emission)

### Provider Layer (Phase 1-3)
- **New type hint?** → Add to `providers/shared/documentation_registry.py` (ONE location)
- **New block key?** → Add to `providers/shared/key_classifications.py` → `BLOCK_KEYS`
- **New UI element?** → Add to `providers/shared/key_classifications.py` → `UI_ELEMENTS`
- **New file type completions?** → Add to `themes/zolo_default.yaml` under `completions`
- **New value completions?** → Add `value_completions` array to key in theme YAML
- **Basic completion feature?** → Update `providers/basic/basic_completion_provider.py`
- **zVAF completion feature?** → Update `providers/zvaf/zvaf_completion_provider.py`
- **New file type routing?** → Update `providers/completion/completion_router.py`

**Architecture Rules:**

**Parser:**
- ✅ Use `parser_service.py` for all parsing (automatic file type routing)
- ✅ Delegate to SSOT modules (`ModifierHandler`, `KeyDetector`, `TokenEmitter`)
- ✅ Use centralized token registry (`token_types.py`, `token_registry.py`)
- ✅ Use data-driven mappings (`UI_ELEMENT_MAPPING`, `SPECIAL_BLOCK_MAPPING`)
- ✅ Use shared helpers (`extract_type_hint()`, `validate_root_key()`)
- ✅ Keep concerns separated (Core → Basic → zVaF layers)
- ❌ Never duplicate parsing logic in grammar files or LSP server
- ❌ Never create parallel implementations (use wrappers/delegation instead)
- ❌ Never hardcode UI element lists (use mappings from `token_registry`)
- ❌ Never duplicate type hint parsing (use `extract_type_hint()`)
- ❌ Never import `tokenize`/`loads` from `parser.py` (use `parser_service.py`)

**Providers (Phase 1-3):**
- ✅ All data comes from SSOT sources (never hardcode)
- ✅ Use `CompletionRouter` for routing (never bypass)
- ✅ Basic provider: lightweight, no file-type overhead
- ✅ zVAF provider: full-featured, theme-driven
- ✅ Source from registries: `documentation_registry`, `key_classifications`
- ✅ Source from theme YAML: key completions, value completions
- ❌ Never hardcode completion values in Python
- ❌ Never duplicate key classifications (use shared modules)
- ❌ Never bypass routing (use `get_completions()` public API)
- ❌ Never create parallel completion implementations

## License

MIT License - See [LICENSE](LICENSE) for details.

## Credits

Built with:
- [pygls](https://github.com/openlawlibrary/pygls) - Python LSP framework
