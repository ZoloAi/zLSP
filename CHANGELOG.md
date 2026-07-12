# Changelog

## [1.2.0] - 2026-07-12

### Added
- `zlsp.bifrost_prism_dir()` — accessor to the pre-built Prism.js bundle, shipped as package data (`zlsp/generated/`); consumed by zOS.zServer at `/zsyntax/<version>/`
- Meta-position diagnostics (`meta_position_validators.py`) with unit coverage
- zGate registration, media/rich-UI/nav/zLoom vocabulary, zImport token, sigil-value highlighting, multi-language semantic tokens
- Bundle-freshness gate in `test_prism_patterns.py` — CI fails if `zlsp/generated/` drifts from the grammar SSOT

### Changed
- Prism bundle output moved from repo-root `bifrost-prism/` (manual copy into zbifrost-client) to packaged `zlsp/generated/` — deployed highlighting now always matches the installed zolo-lsp
- Prism CSS header embeds the package version instead of a wall-clock timestamp (deterministic output)
- zSpark semantic highlighting parked (rebuilt from scratch); only the zPath value override remains
- zRBAC deprecated in favor of zGate

### Fixed
- Parser preserves scalar dash-item commas and zOS ordered-list markers
- YAML block-mapping zDialog fields flagged by diagnostics

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
