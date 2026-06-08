# bifrost-prism — generated Prism.js bundle (manual handoff)

This directory is the **single committed output** of the zLSP Prism generators.
It is **not** auto-deployed. Nothing in zLSP reaches into other repos.

## Contents

| File | Source generator |
| --- | --- |
| `prism-zolo.js` + `prism-{zspark,zui,zschema,zconfig,zenv}.js` | `python3 -m zlsp.generators.generate_prism_zolo` (patterns, from parser SSOT) |
| `prism-zolo-theme.css` | `python3 -m zlsp.themes.generators.prism` (colors, from `zlsp/themes/zolo_default.yaml`) |

Or generate both at once: `zlsp-generate-prism`.

## Handoff (manual, deliberate)

1. **Build** here in zLSP (commands above).
2. **Copy** `bifrost-prism/*` → `zbifrost-client/syntax/` (the canonical
   client-owned prism dir; loaded by `L1_Foundation/bootstrap/prism_loader.js`).
3. **Push + bump** `zbifrost-client`, then update the CDN pin in consumers
   (`zCloud/templates/zVaF.html`, `zGuard …/bridge_connection.py`).

Do not re-add auto-copies into `zCloud/static/`, `zOS/bifrost/`, or `zOS/zTheme/` —
that drift is exactly what this layout removes.
