# zLSP Design Philosophy

**Why zLSP exists and the principles that guide its design.**

---

**zLSP** isn't just a language server—it's a deliberate rethinking of how declarative files should work in the age of AI-assisted development. Four core principles drive every decision:

1. **Single Source of Truth** - Parser rules define syntax once, everything derives from them
2. **String-First Philosophy** - Values default to strings, not numbers (inverts YAML/JSON assumptions)
3. **Live LSP Features** - Parser processes files in real-time (diagnostics, hover, completion)
4. **Static Grammar Generation** - Parser rules generate editor grammars via build commands (aligned by version)

These aren't arbitrary choices. They solve real problems in modern development workflows.

## Design Principles

### 1. Single Source of Truth

**The parser is the only place that understands .zolo syntax.** Everything else asks the parser.

This means:
- **No grammar files** - No TextMate grammars, no Vim syntax files
- **No duplication** - Parsing logic exists in exactly one place
- **Always in sync** - All editors get the same behavior automatically

**Why this matters:**
- Traditional approach: Parser + separate grammar files → inevitable drift, bugs
- Our approach: Parser only → change once, works everywhere

### 2. String-First Philosophy

**The core .zolo innovation: everything is a string unless it's obviously a number or boolean.**

**Strings (the default):**
```zolo
# No type hint needed - it's a string
name: Zolo              # → "Zolo"
version: 1.0.0          # → "1.0.0" (string, not a valid number)
country: NO             # → "NO" (string, not boolean)
msg(str): true          # → "true" (string, because of forced typehint)
```

**Numbers auto-detected:**
```zolo
# Valid numbers automatically parse as numbers
port: 8080              # → 8080 (integer)
ratio: 1.5              # → 1.5 (float)

# But you can force them to strings
version(str): 1.0       # → "1.0" (string, not float)
id(str): 12345          # → "12345" (string, not integer)
```

**Booleans auto-detected:**
```zolo
# Only true/false/null work (lowercase only)
enabled: true           # → true (boolean)
disabled: false         # → false (boolean)
empty: null             # → null

# No YAML quirks: yes/no/on/off/YES/NO don't work
```

## Why this matters

Most real-world declarative files are **string-heavy by nature**.

In JSON, YAML, and TOML, the majority of values represent:
- identifiers
- paths
- versions
- commands
- labels
- environment variables
- free-form text

Yet these formats treat strings as a *special case*—requiring quotes, escaping rules, or ambiguous inference—while optimizing their syntax around numbers and structural types.

`.zolo` inverts that assumption.

### String-First as a UX Decision

`.zolo` is designed from **how declarative files are actually written**, not from abstract type theory.

- Humans think in strings when configuring systems
- LLMs emit strings by default
- Most configuration values are ultimately consumed as strings at runtime

By making **strings the default**, `.zolo` removes friction at the point of authorship and interpretation.

You don’t quote unless you want to.  
You don’t escape unless you need to.  
You don’t fight the format to express intent.

### Explicit Types Where They Matter

Numbers and booleans are still supported—but only when they are **unambiguous** or **explicitly declared**.

This ensures:
- predictable parsing
- immediate feedback on errors
- no context-dependent coercion
- no hidden or surprising behavior

Explicit always beats implicit.

### Designed for the LLM Era

String-first is also a **practical optimization for AI-assisted workflows**.

- LLMs operate natively on text
- Declarative files are frequently embedded directly in prompts
- Every quote, escape, and delimiter consumes tokens

By minimizing syntactic noise, `.zolo`:
- reduces token usage
- preserves semantic clarity
- improves round-trip stability between humans, tools, and models

### Tooling Follows Philosophy

String-first eliminates ambiguity, which makes better tooling possible.

**Better diagnostics:**
- Parser knows exactly what `version: 1.0` will be (float)
- Can warn: "Did you mean `version(str): 1.0`?"
- YAML/JSON tools can't do this (too many edge cases)

**Better hover info:**
- Shows actual type: "This is a number. Add (str) to force string."
- No vague "depends on context" answers

**Better completion:**
- Suggests type hints based on what parser detected
- Confident, not guessing

**The compounding effect:**

Less ambiguity → confident parser → precise feedback → better developer experience

String-first isn't just UX - it's what makes reliable LSP features possible.

### 3. Live LSP Features

**Real-time parsing for advanced editor features.** The LSP server queries the parser on every change.

**What happens live:**
- You type → parser tokenizes immediately
- Diagnostics appear as you type (errors, warnings)
- Hover over keys → parser provides context
- Trigger completion → parser suggests valid options

**How it works:**
1. File opens → `tokenize()` parses content
2. File changes → cache invalidates, re-parse
3. Editor requests (hover, completion) → query cached parse result
4. All editors get identical results (same parser, same logic)

**Supported editors:**
- Vim/Neovim (full LSP)
- VSCode (full LSP)
- Cursor (full LSP)
- Any LSP-compatible editor

### 4. Static Grammar Generation

**Build-time grammar generation ensures alignment.** Parser rules generate editor-specific grammar files.

**What's static:**
- Vim syntax files (`.vim`)
- VSCode TextMate grammar (`.tmLanguage.json`)
- Generated once per zlsp version
- Provides fallback highlighting without LSP

**How it works:**
1. Parser rules define syntax patterns (source of truth)
2. `zolo_default.yaml` defines colors/styles
3. Generator commands (`vim.py`, `vscode.py`) build grammars
4. Grammars bundled with zlsp installation
5. Updated when you upgrade zlsp versions

**Why this matters:**
- Grammars and parser stay aligned (generated from same rules)
- No manual grammar maintenance
- No drift between editors

## The Bigger Picture

These three principles compound into something unique:

**Traditional approach:**
- Write grammar files for each editor
- Parse in one place, highlight in another
- Numbers by default, strings as special case
- Inevitable drift between implementations

**zLSP approach:**
- Parser generates grammars automatically
- Parse once, use everywhere
- Strings by default, numbers explicit
- Perfect consistency by design

**The result:**
- Faster development (no grammar maintenance)
- Better DX (predictable, no surprises)
- AI-friendly (minimal tokens, maximal clarity)
- Future-proof (add editors without rewriting)

**String-first + SSOT + editor-agnostic = a declarative format built for 2026 and beyond.**

## Next Steps

**Ready to try it?** See [README.md](../README.md) for installation and quick start.

**Want technical details?** See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system design.

**Questions or feedback?** Open an issue on [GitHub](https://github.com/ZoloAi/ZoloMedia/issues).

