# zLSP Editors — Vim, VSCode, Cursor

One LSP server, three first-class integrations. All editors talk to the same
`zolo-lsp` process over stdio and therefore behave identically; the per-editor
work is only *client wiring* and *fallback grammars*.

## Install / Uninstall

```bash
zlsp-install-all          # everything (+ Prism regeneration)
zlsp-install-vim | zlsp-install-vscode | zlsp-install-cursor
zlsp-uninstall-all        # or per-editor equivalents
```

## Vim / Neovim (`zlsp/editors/vim/`)

Installs into `~/.vim/` (or `~/.config/nvim/`):

| File | Role |
|------|------|
| `ftdetect/zolo.vim` | `.zolo` → `filetype=zolo` |
| `ftplugin/` + `after/ftplugin/` | settings + LSP client hookup |
| `syntax/zolo.vim` | **generated** fallback highlighting (no LSP needed) |
| `indent/zolo.vim` | indentation rules |

- **Neovim 0.8+**: built-in LSP, zero config.
- **Vim 9+**: needs the `vim-lsp` plugin (install it, then rerun
  `zlsp-install-vim`).
- **Vim 8 and older**: fallback syntax only.

The syntax file is generated from the theme SSOT by
`zlsp/themes/generators/vim.py` — never hand-edited.

## VSCode & Cursor (`zlsp/editors/vscode|cursor/` + `_shared/`)

Cursor is a VSCode fork, so both use one shared installer base
(`_shared/vscode_base.py`) and identical extension formats. Installed to
`~/.vscode/extensions/zolo-lsp-<version>/` (or `~/.cursor/...`): manifest,
LSP client, generated TextMate grammar, and semantic color theme.

### Clean-slate installs (deliberate behavior)

The installer **removes every old `zolo-lsp-*` extension directory** before
installing the current version. This is not housekeeping cosmetics — it
guarantees all generated files (grammars, semantic colors) are regenerated
from the current theme SSOT, so a theme change can never half-propagate and
leave editors disagreeing about colors.

## Language IDs & Icons

The base language id is `zolo` (green icon). On top of it, **sibling language
ids** share the same grammar + LSP but carry their own explorer icon by
filename glob:

| Language id | Matches | Icon |
|-------------|---------|------|
| `zolo` | any `.zolo` (incl. `zSpark.*`) | base green |
| `zolo-ui` | `zUI.*.zolo` | ui |
| `zolo-env` | `zEnv.*.zolo` | env |
| `zolo-server` | `zServer.*.zolo` | server |
| `zolo-raven` | `zRaven.*.zolo`, `**/zRaven/*.zolo` | raven |

Note: these are **editor-side roles** — the parser's `FileType` enum is a
separate classification (see [Grammar_GUIDE](Grammar_GUIDE.md)); `zServer.*`
files, for example, have an editor role but no dedicated parser FileType.

## Troubleshooting

- **Vim**: `:set filetype?` → `zolo`; `:LspInfo` / `:LspStatus` → `zolo-lsp`
  attached. Wrong? Rerun `zlsp-install-vim`.
- **VSCode/Cursor**: status bar shows "Zolo Language Server"; server log under
  View → Output → "Zolo Language Server". Extension missing? Check
  `~/.vscode/extensions/` for a `zolo-lsp-<version>` dir and reinstall.
- **Colors differ between editors**: reinstall (`zlsp-install-all`) — that
  regenerates everything from the SSOT. If it persists, a token mapping is
  missing in a generator: see [Themes_GUIDE](Themes_GUIDE.md), rule 2.

## See Also

- [Installation_GUIDE](Installation_GUIDE.md) — full setup walkthrough
- [Themes_GUIDE](Themes_GUIDE.md) — why generated grammars, never hand-written
