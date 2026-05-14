# Multi-Language Prism.js Generator

Generates Prism.js syntax highlighting definitions for all zolo file types from zlsp SSOT.

## Overview

This generator creates **6 separate Prism.js language definitions**, each optimized for a specific `.zolo` file type:

| Language | Code Fence | File Pattern | Description |
|----------|-----------|--------------|-------------|
| `zolo` | ````zolo` | Generic | REPL and generic files with standard root/nested keys |
| `zspark` | ````zspark` | `zSpark.*.zolo` | Application entry point - `zSpark:` root only, all nested lavender |
| `zui` | ````zui` | `zUI.*.zolo` | UI components - `zMeta:`, `zVaF:`, UI elements (`zH1`, `zText`, etc.) |
| `zschema` | ````zschema` | `zSchema.*.zolo` | Data schemas - table names, field properties (`type`, `pk`, `rules`) |
| `zconfig` | ````zconfig` | `zConfig.*.zolo` | System config - `zMachine:`, locked/editable sections |
| `zenv` | ````zenv` | `zEnv.*.zolo` | Environment - uppercase config, `ZNAVBAR:`, zPath values |

## Architecture

```
zlsp SSOT                          Generated Languages (JS patterns)
─────────────────────             ─────────────────────────────────
key_detector.py                    prism-zolo.js (generic)
token_types.py         ──────>     prism-zspark.js
token_registry.py                  prism-zui.js
file_type_detector.py              prism-zschema.js
                                   prism-zconfig.js
                                   prism-zenv.js

zlsp Theme YAML                    Generated CSS (colors)
─────────────────────             ─────────────────────
zolo_default.yaml      ──────>     prism-zolo-theme.css
(via themes/generators/prism.py)
```

**Key architectural separation:**
- **Patterns (JS)**: Derived from parser SSOT (this directory)
- **Colors (CSS)**: Derived from theme YAML (zlsp/themes/generators/prism.py)

### Components

- **`file_type_pattern_extractor.py`**: Extracts file-type-specific token detection logic from `KeyDetector`
- **`prism_pattern_transformer.py`**: Transforms zlsp patterns to Prism-compatible regex
- **`prism_pattern_generator.py`**: Orchestrates pattern generation for each file type
- **`generate_prism_zolo.py`**: Main script that generates all 6 languages

## Usage

### Generate All Languages (Recommended)

```bash
# Using CLI command (recommended)
zlsp generate-prism

# Or using module directly
cd /Users/galnachshon/Projects/ZoloMedia
python3 -m zlsp.generators.generate_prism_zolo
```

**Output:**

```
zlsp/generated/
  ├── prism-zolo.js      (canonical source)
  ├── prism-zspark.js
  ├── prism-zui.js
  ├── prism-zschema.js
  ├── prism-zconfig.js
  └── prism-zenv.js

zOS/bifrost/src/syntax/
  └── (copies for dev reference)

zCloud/static/js/
  └── (copies for runtime - served at /static/js/)
```

### Run Tests

```bash
# Unit tests
python3 -m pytest zlsp/tests/unit/test_prism_generator.py -v

# Integration tests
python3 -m pytest zlsp/tests/integration/test_prism_patterns.py -v

# Visual browser test
open zlsp/tests/browser/test_all_languages.html
```

## File Type Specific Patterns

### zSpark (Application Entry Point)

**Root keys:**
- `zSpark:` → GREEN (function) - only special root
- Others → PINK (class-name) - generic roots

**Nested keys:**
- ALL keys under `zSpark:` → LAVENDER (variable)

**Values:**
- `zCLI`, `zBifrost` → RED (constant) - zMode values
- `@.path`, `~.path` → CYAN (string) - zPath references

**Example:**

```zspark
zSpark:
    title: MyApp          # LAVENDER
    zMode: zCLI           # zCLI = RED
    zPath: @.config       # CYAN
```

### zUI (User Interface)

**Root keys:**
- `zMeta:`, `zVaF:` → GREEN (function)
- Others → PINK (class-name)

**Nested keys:**
- `zH1-zH6:`, `zText:`, `zMD:`, `zImage:` → BLUE/YELLOW (function) - UI elements
- `label:`, `content:`, `src:`, `href:` → LAVENDER (variable) - element properties
- `_zClass:`, `_zStyle:`, `_zHTML:` → YELLOW (keyword) - bifrost metadata
  - `_zStyle:` supports inline string: `_zStyle: color: red; font-size: 16px`
  - `_zStyle:` supports nested object: `_zStyle:\n    color: red\n    font-size: 16px`
- `zWizard:` → GREEN (function) - control flow
- `zRBAC:` → RED (constant) - access control

**Example:**

```zui
zMeta:                    # GREEN
    zNavBar: true

zVaF:                     # GREEN
    zH1:                  # BLUE (UI element)
        label: Welcome    # LAVENDER (property)
        _zClass: title    # YELLOW (bifrost)
```

### zSchema (Data Schema)

**Root keys:**
- `zMeta:` → GREEN (function)
- Table names → PINK (class-name)

**Nested keys:**
- Under `zMeta`: `Data_Type:`, `Schema_Name:` → PURPLE (keyword) - zOS data keys
- Field names (indent 1) → DEFAULT
- Field properties (indent 2+): `type:`, `pk:`, `rules:` → PURPLE (keyword)

**Example:**

```zschema
zMeta:                    # GREEN
    Data_Type: SQL        # PURPLE

users:                    # PINK (table name)
    id:                   # default
        type: int         # PURPLE
        pk: true          # PURPLE
```

### zConfig (System Configuration)

**Root keys:**
- `zMachine:`, `Z[A-Z0-9_]+:` → GREEN (function)
- Others → PINK (class-name)

**Nested keys:**
- Locked sections (indent 1): `machine_identity:`, `python_runtime:` → RED (constant)
- Editable sections (indent 1): `user_preferences:`, `time_date_formatting:` → BLUE (variable)
- Properties (indent 2+) → LAVENDER (variable)

**Example:**

```zconfig
zMachine:                    # GREEN
    machine_identity:        # RED (locked)
        os: Darwin
    user_preferences:        # BLUE (editable)
        theme: dark          # LAVENDER
```

### zEnv (Environment Configuration)

**Root keys:**
- `DEPLOYMENT:`, `DEBUG:`, `LOG_LEVEL:` → PURPLE (keyword) - config roots
- `ZNAVBAR:`, `ZSERVER_MOUNTS:` (Z-uppercase) → GREEN (function)
- Others → PINK (class-name)

**Nested keys:**
- Under `ZNAVBAR` (indent 1) → ORANGE (type) - navbar items
- `zSub:` (grandchild+) → PURPLE (keyword) - submenu
- `zRBAC:` → RED (constant) - access control

**Values:**
- `@.path`, `~.path` → CYAN (string) - zPath references
- `DEBUG`, `PROD`, `INFO`, etc. → YELLOW (number) - env constants

**Example:**

```zenv
DEPLOYMENT: Production    # PURPLE: YELLOW
ZNAVBAR:                  # GREEN
    Home:                 # ORANGE
        zPath: @.home     # CYAN
    Admin:
        zSub:             # PURPLE
            Users: @.users
```

## Pattern Transformation

### Multiline Context Handling

**Problem:** zlsp parses line-by-line; Prism.js processes entire code blocks.

**Solution:** Transform line-start anchors `^` to handle newlines:

```python
# zlsp pattern
^[A-Z][a-zA-Z0-9_]*:

# Prism pattern
/((?:^|\n)[ \t]*)[A-Z][a-zA-Z0-9_]*(?=\s*(?:\([^)]+\))?[*!^~]?:)/m
```

### Pattern Ordering

Prism processes patterns sequentially. Order matters:

1. **Comments** (highest priority - match anywhere)
2. **Specific root keys** (`zSpark:`, `zMeta:`) before generic `root-key`
3. **Specific nested keys** (UI elements, field properties) before generic `property`
4. **Type hints and modifiers**
5. **Values** (strings, numbers, booleans)
6. **Punctuation** (lowest priority)

Implemented in `prism_pattern_transformer.py::optimize_pattern_order()`.

## Limitations & Workarounds

### 1. No Block Context Tracking

**Problem:** zlsp tracks `is_inside_block('zSpark')`, Prism can't.

**Workaround:** Use indentation-based approximation + specific language per file type.

```python
# zlsp: context-aware
if emitter.is_inside_block('zSpark', indent):
    return TokenType.ZSPARK_NESTED_KEY

# Prism: indentation-based
'zspark-nested': {
    pattern: /(?<=\n)[ \t]+[a-zA-Z][a-zA-Z0-9_]*(?=\s*(?:\([^)]+\))?:)/m
}
```

### 2. Dynamic Component Names

**Problem:** zlsp detects `zUI.MyComponent.zolo` and colors `MyComponent:` as `ZMETA_KEY`.

**Workaround:** Only match known special roots (`zMeta`, `zVaF`). Custom components fall through to generic `root-key`.

### 3. Value-Type Detection

**Problem:** zlsp detects `zMode: zCLI` and colors `zCLI` as `ZSPARK_MODE_VALUE`.

**Current:** Limited value patterns (zCLI, zBifrost, DEBUG, PROD).

**Future:** Expand as needed.

## Testing

### Unit Tests (`tests/unit/test_prism_generator.py`)

- Pattern extraction for each file type
- Pattern ordering optimization
- JavaScript definition building
- Regression test for `Settings_Page:` bug

### Integration Tests (`tests/integration/test_prism_patterns.py`)

- Generator pipeline execution
- All 6 files generated correctly
- Files synchronized between `generated/` and `bifrost/`
- Language-specific patterns present
- File syntax validity

### Browser Test (`tests/browser/test_all_languages.html`)

Visual validation with side-by-side examples of all 6 languages.

**Features:**

- Color legend
- Load status indicator
- Test cases for each file type
- Regression test for Settings_Page bug

## Regeneration

**When to regenerate:**

- After updating `KeyDetector` token detection logic
- After adding new `TokenType` values
- After modifying `TokenRegistry` special key sets
- When zlsp syntax rules change

**Always regenerate and run tests after zlsp SSOT changes:**

```bash
python3 -m zlsp.generators.generate_prism_zolo
python3 -m pytest zlsp/tests/ -v
open zlsp/tests/browser/test_all_languages.html
```

## Migration Path

### Phase 1: Generation (Current)

- ✅ Generate all 6 languages
- ✅ Tests pass for all file types
- ✅ Browser visual validation

### Phase 2: Documentation (Next)

- Update code fences in `.zolo` documentation files
- Change generic ````zolo` to specific ````zspark`, ````zui`, etc.

**Files to update:**

- `zCloud/UI/zProducts/zOS/Overview/zUI.zFundamentals.zolo`
- `zCloud/UI/zProducts/zOS/Overview/zUI.zVaFiles.zolo`
- Other documentation with code examples

### Phase 3: Auto-Detection (Future)

Enhance `text_renderer.js` to auto-detect language from content:

```javascript
function detectZoloLanguage(code) {
    if (/^zSpark:/.test(code)) return 'zspark';
    if (/^zMeta:|^zVaF:/.test(code)) return 'zui';
    if (/^DEPLOYMENT:|^DEBUG:|^ZNAVBAR:/.test(code)) return 'zenv';
    // ... etc
    return 'zolo';  // fallback to generic
}
```

## File Structure

```
zlsp/zlsp/generators/
├── __init__.py                          # Package init
├── README.md                            # This file
├── file_type_pattern_extractor.py       # Extract KeyDetector logic per file type
├── prism_pattern_transformer.py         # Transform zlsp → Prism regex
├── prism_pattern_generator.py           # Orchestrate pattern generation
└── generate_prism_zolo.py               # Main generator script

zlsp/generated/                          # Canonical source (generated)
├── prism-zolo.js
├── prism-zspark.js
├── prism-zui.js
├── prism-zschema.js
├── prism-zconfig.js
└── prism-zenv.js

zOS/bifrost/src/syntax/                  # Dev reference (copied)
└── (same 6 files)

zCloud/static/js/                        # Runtime location (copied)
└── (same 6 files - served at /static/js/)

zlsp/tests/
├── unit/test_prism_generator.py         # Unit tests
├── integration/test_prism_patterns.py   # Integration tests
└── browser/test_all_languages.html      # Visual browser test
```

## Success Criteria

- [x] Generator creates 6 language files from zlsp SSOT
- [x] Each language has file-type-specific patterns from KeyDetector
- [x] `zSpark:` colors as green in zspark language (not pink)
- [x] All nested keys under `zSpark:` color as lavender in zspark language
- [x] UI elements (`zH1`, `zText`) color correctly in zui language
- [x] zSchema field properties (`type`, `pk`) color as purple in zschema language
- [x] All 6 languages load in browser without errors
- [x] All tests pass (94 total: 23 unit + 71 integration)
- [x] Settings_Page regression test passes
