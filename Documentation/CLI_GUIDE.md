# zlsp CLI Guide

Reference for the `zlsp` command-line interface.

```bash
zlsp <command> [options]
```

| Command | Purpose |
|---------|---------|
| `verify` | Installation health check |
| `test` | Run the test suite |
| `server` | Start the LSP server (usually editor-invoked) |
| `info` | Package information |
| `generate-prism` | Regenerate the Prism.js web-highlighting bundle |

---

## zlsp verify

```bash
zlsp verify              # quick health check
zlsp verify --verbose    # detailed (includes example files)
```

Checks: Python version (3.8+), dependencies (pygls, lsprotocol), parser
round-trip (`loads`/`dumps`), LSP server availability, semantic tokenizer,
and detected editor integrations. Exit code `0` = all passed, `1` = failures.

Use it after install, after upgrades, and before reporting bugs.

## zlsp test

```bash
zlsp test                # full suite
zlsp test --quick        # unit + integration, skip slow e2e
zlsp test --unit | --integration | --e2e
zlsp test --coverage     # terminal + HTML report (htmlcov/)
zlsp test -k <pattern>   # by test name
zlsp test -x             # fail fast
zlsp test -v             # verbose
```

Typical loops: `zlsp test --quick -x` while iterating; `zlsp test --coverage`
before a release. Requires dev deps (`pip install "zolo-lsp[dev]"` or
`pip install pytest`).

## zlsp server

```bash
zlsp server
```

Starts the LSP server on **stdio**. Editors invoke this via the `zolo-lsp`
entry point themselves — manual runs are for debugging only:

```bash
zlsp server 2> lsp_stderr.log
```

(The server is stdio-only; there is no TCP/port mode.)

## zlsp info

```bash
zlsp info
```

Prints version (current: 1.2.0), install location, feature list, and the
command table.

## zlsp generate-prism

```bash
zlsp generate-prism                 # patterns + CSS
zlsp generate-prism --patterns-only # JS patterns only
zlsp generate-prism --css-only      # CSS theme only
```

Contributor command — regenerates the packaged web-highlighting bundle from
the parser + theme SSOTs. End users never need it (the bundle ships in the
wheel). Details: [Prism_GUIDE](Prism_GUIDE.md).

---

## Common Workflows

```bash
# First-time setup
pip install zolo-lsp && zlsp verify && zlsp-install-all

# Development loop
zlsp test --quick -x
zlsp test -k hover

# Troubleshooting
zlsp verify --verbose
zlsp info
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `pytest not installed` | `pip install "zolo-lsp[dev]"` |
| missing pygls/lsprotocol | `pip install --upgrade zolo-lsp` |
| no editor integrations detected | run `zlsp-install-<editor>` |
| Python too old | upgrade to 3.8+ |
| parser check fails | `pip install --force-reinstall zolo-lsp` |
| `zolo-lsp` not on PATH | `export PATH="$HOME/.local/bin:$PATH"` |

All commands exit `0` on success, `1` on failure — script-friendly:

```bash
zlsp verify || exit 1
```

## See Also

- [Installation_GUIDE](Installation_GUIDE.md)
- [Prism_GUIDE](Prism_GUIDE.md)
- [Documentation index](README.md)
