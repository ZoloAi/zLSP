# Changelog

## [Unreleased]

### Added
- **Color Ledger Documentation**: Created comprehensive `Documentation/COLOR_LEDGER.md` showing all tokens, colors, and usage across file types
  - Complete token reference with IDs, colors (hex, ANSI, RGB)
  - Organized by file type (Basic, zSpark, zEnv, zUI, zSchema, zConfig)
  - Misalignment analysis and recommendations
  - Visual hierarchy breakdown
- **Prism.js CLI Command**: Added `zlsp generate-prism` command for web syntax highlighting generation
  - `zlsp generate-prism` - Generate both patterns and CSS
  - `zlsp generate-prism --patterns-only` - JS patterns only
  - `zlsp generate-prism --css-only` - CSS theme only
  - Standalone command: `zlsp-generate-prism`
- **Prism Generation in install-all**: `zlsp-install-all` now automatically generates Prism.js files
- **Architecture Documentation**: Created `zlsp/generators/ARCHITECTURE.md` documenting pattern vs color separation
- **CLI Usage Guide**: Created `zlsp/generators/CLI_USAGE.md` for Prism generation reference

### Changed
- **Prism Architecture Refactor**: Separated Prism.js generation into two concerns:
  - **Patterns (JS)**: Generated from parser SSOT (`zlsp/generators/generate_prism_zolo.py`)
  - **Colors (CSS)**: Generated from theme YAML (`zlsp/themes/generators/prism.py`)
  - Removed hardcoded patterns from theme generator
  - Renamed `PrismGenerator` → `PrismCSSGenerator` (CSS only)
  - Deprecated `_generate_prism_language()` method (use SSOT-based generator instead)
- **Documentation Updates**:
  - Updated README.md with `zlsp-generate-prism` command
  - Updated INSTALLATION.md to reflect install-all includes Prism
  - Updated generators/README.md with CLI usage examples
  - Updated generators/ARCHITECTURE.md with clear separation of concerns

### Fixed
- **Architectural Misalignment**: Prism.js no longer treated like an IDE
  - Prism patterns now derived from parser SSOT (single source of truth)
  - Clear separation: IDEs need colors, Prism needs patterns + colors
  - 6 language-specific files (zolo, zspark, zui, zschema, zconfig, zenv)

## Architecture Changes

### Before (WRONG)
```
zlsp/themes/generators/prism.py
├─ Hardcoded JS patterns (lines 54-231)
└─ Generated: prism-zolo.js + CSS
```

### After (CORRECT)
```
zlsp/generators/generate_prism_zolo.py
└─ Generates: 6 JS files (patterns from parser SSOT)

zlsp/themes/generators/prism.py
└─ Generates: CSS only (colors from theme YAML)
```

### Impact
- **Single Source of Truth**: Pattern rules live ONLY in parser
- **File-Type Specialization**: 6 languages instead of 1 generic
- **Automatic Sync**: Parser changes → regenerate → Prism updated
- **Testability**: 95 tests validate generation (23 unit + 72 integration)

## Migration Notes

### For Users
- Old command still works: `python3 -m zlsp.generators.generate_prism_zolo`
- New command recommended: `zlsp generate-prism`
- `zlsp-install-all` now includes Prism generation

### For Developers
- Don't use `zlsp/themes/generators/prism.py` for patterns
- Use `zlsp/generators/generate_prism_zolo.py` for patterns
- Use `zlsp/themes/generators/prism.py` ONLY for CSS colors
- Regenerate after parser changes: `zlsp generate-prism --patterns-only`
- Regenerate after theme changes: `zlsp generate-prism --css-only`
