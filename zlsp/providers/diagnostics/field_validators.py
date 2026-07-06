"""
Field Validator — zLSP diagnostic for unsupported block-mapping zDialog fields.

`.zolo` is string-first, NOT YAML. A YAML-style block mapping inside a list item:

    fields:
        - name: age
          type: number

is NOT understood by the zParser — it line-joins the entry into a single string
(`'name: age type: number'`), which then becomes a literal field NAME. The field
silently loses its real name, its `type`, and ALL type validation. The runtime
cannot distinguish this from intent (it just joins text), so author-time is the
only place to catch it.

The supported form is the inline flow dict:

    fields:
        - {name: age, type: number, required: false}

Scope: only `fields:` blocks whose nearest parent is `zDialog:` — the `-` block
syntax stays valid everywhere else in `.zolo`.

Emits DiagnosticSeverity.Error — in a zDialog this is always broken, never
intentional.
"""

import re
from typing import List

from lsprotocol import types as lsp_types


# ── constants ────────────────────────────────────────────────────────────────

# A `fields:` key with NO inline value (block list follows on later lines).
_FIELDS_BLOCK_RE = re.compile(r"^(\s*)fields\s*:\s*(#.*)?$")

# Any key line (indent + bare key + colon) — used for parent-scope detection.
_KEY_LINE_RE = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_\-]*)\s*:")

# A list item that opens a block mapping: dash + key + colon, NOT inline `{…}`.
#   - name: age      → match (bad)
#   - {name: age}    → no match (inline flow dict, ok)
#   - name           → no match (bare, ok)
_BLOCK_MAP_ITEM_RE = re.compile(r"^(\s*)-\s*(?!\{)([A-Za-z_][A-Za-z0-9_\-]*)\s*:")

_FIX_HINT = "{name: age, type: number, required: false}"


# ── helpers ──────────────────────────────────────────────────────────────────

def _indent_level(line: str, tab_size: int = 4) -> int:
    """Count leading spaces (tabs expanded to tab_size)."""
    n = 0
    for ch in line:
        if ch == " ":
            n += 1
        elif ch == "\t":
            n += tab_size
        else:
            break
    return n


def _parent_is_zdialog(lines: List[str], fields_idx: int, fields_indent: int) -> bool:
    """True if the nearest lower-indent key above `fields:` is `zDialog:`."""
    for prev_idx in range(fields_idx - 1, -1, -1):
        prev_line = lines[prev_idx]
        if not prev_line.strip() or prev_line.strip().startswith("#"):
            continue
        if _indent_level(prev_line) < fields_indent:
            km = _KEY_LINE_RE.match(prev_line)
            return bool(km and km.group(2) == "zDialog")
    return False


def _make_error(line_no: int, col_start: int, col_end: int, msg: str) -> lsp_types.Diagnostic:
    return lsp_types.Diagnostic(
        range=lsp_types.Range(
            start=lsp_types.Position(line=line_no, character=col_start),
            end=lsp_types.Position(line=line_no, character=col_end),
        ),
        message=msg,
        severity=lsp_types.DiagnosticSeverity.Error,
        source="zolo-lsp",
    )


# ── main entry ───────────────────────────────────────────────────────────────

def validate_dialog_fields(content: str) -> List[lsp_types.Diagnostic]:
    """
    Flag YAML-style block-mapping list items under a zDialog `fields:` block.

    Returns a list of Error diagnostics (may be empty).
    """
    lines = content.splitlines()
    diagnostics: List[lsp_types.Diagnostic] = []

    for line_idx, line in enumerate(lines):
        fields_match = _FIELDS_BLOCK_RE.match(line)
        if not fields_match:
            continue

        fields_indent = _indent_level(line)
        if not _parent_is_zdialog(lines, line_idx, fields_indent):
            continue

        # Scan the block body: lines indented deeper than `fields:`.
        for body_idx in range(line_idx + 1, len(lines)):
            body_line = lines[body_idx]
            if not body_line.strip() or body_line.strip().startswith("#"):
                continue
            if _indent_level(body_line) <= fields_indent:
                break  # block ended

            item_match = _BLOCK_MAP_ITEM_RE.match(body_line)
            if item_match:
                col_start = len(item_match.group(1))  # at the dash
                diagnostics.append(
                    _make_error(
                        body_idx,
                        col_start,
                        len(body_line),
                        "zDialog field uses an unsupported block-mapping "
                        "('- key: value'). .zolo is string-first, not YAML — this "
                        "is silently joined into one string and loses the field "
                        f"name, type, and validation. Use the inline form: - {_FIX_HINT}.",
                    )
                )

    return diagnostics
