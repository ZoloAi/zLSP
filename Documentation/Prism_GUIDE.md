# zLSP Prism — Web Syntax Highlighting

How `.zolo` highlighting reaches the browser: a pre-built Prism.js bundle,
generated from the same parser SSOT as everything else, **shipped inside the
wheel** — end users never generate anything.

## The Bundle

Packaged at `zlsp/generated/`:

```
prism-zolo.js       generic .zolo          prism-zschema.js   zSchema.*
prism-zspark.js     zSpark.*               prism-zconfig.js   zConfig.*
prism-zui.js        zUI.*                  prism-zenv.js      zEnv.*
prism-zolo-theme.css   ← colors, from the theme SSOT
```

Six language definitions (one per file type, each with its own pattern set)
plus one CSS theme.

## The Accessor — `zlsp.bifrost_prism_dir()`

```python
import zlsp
bundle = zlsp.bifrost_prism_dir()   # Path to the packaged bundle
```

This is the **contract consumed by zOS.zServer**, which mounts the directory
read-only at `/zsyntax/<version>/` for zBifrost pages. Because the bundle is
generated at **build time** — never at runtime — it always matches the
installed package's grammar version.

Failure semantics are deliberate:

- `AttributeError` → old zlsp without the accessor
- `FileNotFoundError` → new zlsp but a damaged install (bundle missing)

Callers can tell the two apart.

## Generation (contributors only)

```bash
zlsp generate-prism                 # patterns + CSS
zlsp generate-prism --patterns-only
zlsp generate-prism --css-only
```

Pipeline (`zlsp/generators/`):

```
key_detector / token_types / token_registry / file_type_detector  → JS patterns
themes/zolo_default.yaml                                          → CSS theme
```

Patterns derive from the **parser SSOT**; colors derive from the **theme
SSOT**. Never edit the generated files — regenerate.

Deeper dev docs live next to the code and are the authority on generator
internals: `zlsp/generators/README.md`, `ARCHITECTURE.md`,
`SSOT_PRISM_GENERATION.md`, `CLI_USAGE.md`.

## The Pattern-Order Rule

**In Prism.js, the first matching pattern wins.** The generator's
`optimize_pattern_order()` is the SSOT for ordering, and its law is:

1. Specific patterns (numbers, booleans, quoted strings) come **before**
   catch-alls.
2. The unquoted-string catch-all comes **last** — it matches almost anything,
   so anything after it never fires.

(Historical scar: numbers once rendered white on the web because the
catch-all sat above the number pattern. The priority table in the
transformer exists so that class of bug stays dead.)

## Freshness

The bundle regenerates on `zlsp-install-all` and on release builds. If web
highlighting looks stale after upgrading, reinstall the package — do not
hand-patch JS in `generated/`.

## See Also

- [Themes_GUIDE](Themes_GUIDE.md) — where the CSS colors come from
- [Architecture_GUIDE](Architecture_GUIDE.md) — the SSOT chain
