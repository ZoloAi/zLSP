# zLSP Design Philosophy

**Why zLSP exists and the principles that guide its design.**

zLSP isn't just a language server — it's a deliberate rethinking of how
declarative files should work in the age of AI-assisted development. Four
principles drive every decision:

1. **Single Source of Truth** — the parser defines syntax once; everything derives from it
2. **String-First** — values default to strings (inverts YAML/JSON assumptions)
3. **Live LSP Features** — real-time parsing feeds diagnostics, hover, completion
4. **Generated Grammars** — editor grammars are built from the parser, never hand-written

## 1. Single Source of Truth

**The parser is the only component that understands `.zolo` syntax.**
Everything else asks it — or is generated from it.

Grammar files *do exist* (Vim syntax, VSCode TextMate, Prism patterns) — but
they are **build artifacts, generated from the Python SSOT**, never
hand-written or hand-maintained. That's the precise claim:

- Traditional approach: a parser *plus* separately-maintained grammar files
  per editor → inevitable drift, per-editor bugs.
- zLSP approach: parser rules → generators → grammars, aligned by version.
  Change a rule once; regenerate; every editor and the web agree.

## 2. String-First

**Everything is a string unless it's unambiguously a number or boolean.**

```zolo
name: Zolo              # → "Zolo"
version: 1.0.0          # → "1.0.0"  (not a valid number → string)
country: NO             # → "NO"     (no Norway problem)
port: 8080              # → 8080     (unambiguous int)
version(str): 1.0       # → "1.0"    (forced string)
enabled: true           # → true     (lowercase true/false/null only)
```

Most real-world declarative content is string-heavy — identifiers, paths,
versions, commands, labels. JSON/YAML/TOML treat strings as the special case
(quotes, escapes, ambiguous inference) while optimizing for numbers. `.zolo`
inverts that: you don't quote unless you want to, don't escape unless you
need to, and the parser never surprises you with coercion.

**And it's an LLM-era optimization:** models operate on text, configs get
embedded in prompts, and every quote and delimiter costs tokens. Minimal
syntactic noise → fewer tokens, cleaner round-trips between humans, tools,
and models.

**And it's what makes the tooling possible:** because parsing is unambiguous,
the LSP can say *exactly* what `version: 1.0` will become and suggest
`version(str):` when you probably meant a string. YAML tooling can't — too
many context-dependent edge cases.

## 3. Live LSP Features

The server re-tokenizes on every change; diagnostics, hover, and completion
all read the same fresh parse. Every LSP-capable editor gets identical
behavior because there is exactly one parser (see
[Architecture_GUIDE](Architecture_GUIDE.md)).

## 4. Generated Grammars

Build-time generation keeps the fallback layers aligned:

1. Parser rules define the patterns (SSOT)
2. `zolo_default.yaml` defines the colors (SSOT)
3. Generators emit Vim syntax, TextMate grammars, Prism JS/CSS
4. Artifacts ship with the package, versioned with it

Editors get instant fallback highlighting even before the LSP attaches, and
the fallback can't drift from the live behavior because both came from the
same rules.

## The Compounding Effect

Less ambiguity → a confident parser → precise diagnostics and completions →
grammars that can be generated instead of maintained → editors that can't
disagree. Each principle makes the next one cheaper.

**String-first + SSOT + generated grammars = a declarative format built for
the LLM era.**

---

**Try it:** [Installation_GUIDE](Installation_GUIDE.md) ·
**Internals:** [Architecture_GUIDE](Architecture_GUIDE.md) ·
**Feedback:** [github.com/ZoloAi/zLSP/issues](https://github.com/ZoloAi/zLSP/issues)
