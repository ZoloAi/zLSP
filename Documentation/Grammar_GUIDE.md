# zLSP Grammar — File Types, Special Blocks, Diagnostics

How zLSP classifies `.zolo` files and keys, and what each class unlocks.

## File-Type Detection

Filename-based, at the parser-service entry point (before any parsing —
see [Architecture_GUIDE](Architecture_GUIDE.md) for the routing).
SSOT: `zlsp/parser/zvaf/file_type_detector.py`.

| Pattern | FileType | Parser route |
|---------|----------|--------------|
| `zSpark.*.zolo` | `ZSPARK` | zVaF |
| `zEnv.*.zolo` | `ZENV` | zVaF |
| `zUI.*.zolo` | `ZUI` | zVaF |
| `zConfig.*.zolo` | `ZCONFIG` | zVaF |
| `zSchema.*.zolo` | `ZSCHEMA` | zVaF |
| `zRaven.*.zolo` | `ZRAVEN` | zVaF |
| `*.zolo` (anything else) | `GENERIC` | Basic |

Notes:

- The prefix must start the filename: `zSpark.production.zolo` → ZSPARK, but
  `spark.config.zolo` → GENERIC.
- There is **no `ZMACHINE` file type** — `zMachine` survives as a *special
  block* inside files (below), not as a filename class.
- `zServer.*.zolo` route files are recognized on the **editor side** (they get
  the `zolo-server` language id and icon in VSCode/Cursor — see
  [Editors_GUIDE](Editors_GUIDE.md)); the parser treats them through the same
  pipeline.

## What Every File Gets

- **Semantic highlighting** — context-aware token colors
- **Diagnostics** — live errors/warnings as you type
- **Hover documentation** — keys, type hints, gate knobs
- **Indentation validation** — tabs OR spaces, never mixed (Python-style)

Formatting and symbol navigation are **not** currently served — don't expect
them from the LSP client.

## What zVaF Files Add

- **Key modifiers** — `^` `~` `!` `*` prefixes (`modifier_handler.py`)
- **Special blocks** — `zGate`, `zMeta`, `ZNAVBAR`, `zMachine`, `zSpark`
  blocks are recognized and their inner keys classified (`block_manager.py`)
- **UI shorthands** — zUI element sugar (`ui_shortcuts.py`)
- **Auto-multiline** — properties that collect multiline values without fences
- **Context completions** — file-type-aware suggestions (zSpark keys in a
  spark, schema property keys in a zSchema, …)

## zGate (and the zRBAC alias)

**`zGate` is the one gate verb.** `zRBAC` is its **deprecated alias** — still
recognized by the parser (highlighted tomato-red, same treatment) so legacy
files don't break, but new files should write `zGate`. Gate knob keys inside a
`zGate:` block get their own classification (`ZGATE_OPTION_KEYS` in
`token_registry.py`).

## Shared Syntax (all file types)

```zolo
# comment                      inline too
key: value                     # string-first: value is a string
port: 8080                     # unambiguous number → int
port(int): 8080                # explicit type hint
flag(bool): true               # true/false/null only — no yes/no/on/off
logo: @.assets.logo.png        # zPath notation
key: value  #> inline doc <#   # doc comment
```

Indentation: 4 spaces recommended; tabs allowed; mixing is an error.

## Diagnostics

The parser emits diagnostics during tokenization; the LSP relays them live.
Typical classes: mixed indentation, malformed type hints, invalid values for
hinted types, structural errors in special blocks. Formatting of messages
lives in the providers' shared validators — text SSOT in
`providers/shared/documentation_registry.py`.

## Naming & Layout Conventions

```
project/
├── zSpark.app.zolo            # descriptive middle segment
├── config/zConfig.database.zolo
├── ui/zUI.Navbar.zolo
├── schema/zSchema.users.zolo
└── zRaven/zRaven.app.zolo     # test flows
```

Avoid prefix-less names (`config.prod.zolo` parses as GENERIC) and bare
prefixes (`zSpark.zolo` — give it a middle segment).

## See Also

- [Architecture_GUIDE](Architecture_GUIDE.md) — dual-path routing
- [Themes_GUIDE](Themes_GUIDE.md) — what colors those tokens get
- zOS documentation — what these file types *do* at runtime
  ([github.com/ZoloAi/zOS](https://github.com/ZoloAi/zOS))
