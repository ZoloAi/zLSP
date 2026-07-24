# zLSP Themes — the Color SSOT

Every color in every editor comes from **one file**:
`zlsp/themes/zolo_default.yaml`. Nothing else defines colors. This guide
explains the file's shape, the generation pipeline, and the two hard rules
that keep editors visually identical.

## The Pipeline

```
zolo_default.yaml (colors)  +  token_types.py (vocabulary)
        │
        ├── themes/generators/vim.py     → Vim  :highlight groups
        ├── themes/generators/vscode.py  → VSCode/Cursor semantic colors + TextMate theme
        └── generators/ (Prism)          → prism-zolo-theme.css   (see Prism_GUIDE)
```

Generators run at **install time** (`zlsp-install-*`) and at Prism
regeneration — never by hand-editing output files.

## Theme File Shape

`zolo_default.yaml` (~1,100 lines) has two layers:

1. **`palette:`** — named colors defined once, in multiple formats
   (hex / ANSI-256 / RGB) for editor compatibility. Organized as universal
   syntax colors first (strings, numbers, booleans, punctuation), then
   zOS-specific colors (block keys, dispatch keys, raven keys, env states…).
2. **`tokens:`** — one entry per **TokenType** (the vocabulary from
   `token_types.py`), each referencing a palette color. This is the ledger.

## Color Ledger (representative rows)

The full ledger is the `tokens:` section of the YAML — ~60 token types. The
core vocabulary:

| Token | Palette color | Hex | Feel |
|-------|--------------|-----|------|
| `comment` | gray | `#626262` | recede |
| `rootKey` | soft_blue | `#5fafd7` | structure |
| `nestedKey` | mint_green | `#87ffaf` | structure, lighter |
| `colon` | white | `#ffffff` | neutral |
| `string` | light_cream | `#fffbcb` | the default value type |
| `number` | dark_orange | `#FF8C00` | pops |
| `boolean` / null | deep_blue | `#0087ff` | pops, cooler |
| `typeHint` | lavender | — | annotation |
| `typeHintParen` | white | `#ffffff` | neutral frame |
| `dispatchKey` | golden_yellow | — | events |
| `zravenPickKey` | raven_silver | — | test verbs |
| `zrbacKey` (zGate) | tomato red family | — | gates shout |

For exact values, read the YAML — it is deliberately the only place they
exist, so this doc lists the *shape*, not a duplicate copy that would drift.

## The Two Hard Rules

**1. Every visual element needs its own token.**
If the parser emits one blob token for `(int)`, the theme cannot color the
parentheses differently from the hint text. That is why the parser emits
`TYPE_HINT_PAREN` + `TYPE_HINT` + `TYPE_HINT_PAREN` as three tokens. Parser
token emission is layer 1 of the SSOT — if it's wrong, no theme or generator
downstream can fix it.

**2. Every token type needs a mapping in every generator.**
A token that exists in the theme but is missing from a generator's mapping
falls back to that editor's default colors — silently breaking cross-editor
consistency (this bit us with `colon`/`comma` in the Vim generator once).
When adding a token type: theme YAML **and** all generators, in one change.

## Customizing

Copy the YAML, point `ZLSP_THEME` at your copy, restart the server. Supported
but deliberately un-advertised — the value of the SSOT is that every zolo
file looks the same everywhere.

## See Also

- [Architecture_GUIDE](Architecture_GUIDE.md) — where tokens come from
- [Prism_GUIDE](Prism_GUIDE.md) — the web half of this pipeline
- [Editors_GUIDE](Editors_GUIDE.md) — install-time regeneration behavior
