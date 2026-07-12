"""
Meta Position Validator — zLSP diagnostic for a misplaced `zMeta:` block.

`zMeta` is a canonical ROOT-level block — one per `.zolo` file, declared at
indent 0 (zSchema's `zMeta` sits beside its table blocks, zUI's `zMeta` sits
beside its top-level view blocks, zRaven's `zMeta` sits beside `Tests:`, …).
Nesting it inside a block instead (`Main:\n    zMeta: ...`) is NOT the
documented grammar, yet nothing currently rejects it: the runtime happily
reads a nested `zMeta`, and the parser gives it none of a real root `zMeta`'s
handling — it falls through as a plain nested key, indistinguishable from
`label:` or `color:`. Author-time is the only place to catch the drift back
to the canonical shape.

Applies uniformly across every `.zolo` file type (zUI, zSchema, zEnv, zConfig,
zSpark, zRaven) — `zMeta` is never a legitimate nested key in any of them.

Emits DiagnosticSeverity.Error — a misplaced zMeta silently loses its intended
effect, never a stylistic choice.
"""

import re
from typing import List

from lsprotocol import types as lsp_types

# A `zMeta:` key line — bare key + colon, any leading whitespace, optional trailing comment.
_ZMETA_LINE_RE = re.compile(r"^(\s*)zMeta\s*:\s*(#.*)?$")


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


def validate_meta_position(content: str) -> List[lsp_types.Diagnostic]:
    """
    Flag any `zMeta:` block that is NOT at file root (indent 0).

    Returns a list of Error diagnostics (may be empty).
    """
    lines = content.splitlines()
    diagnostics: List[lsp_types.Diagnostic] = []

    for line_idx, line in enumerate(lines):
        match = _ZMETA_LINE_RE.match(line)
        if not match:
            continue

        if _indent_level(line) == 0:
            continue  # correctly at file root

        col_start = len(match.group(1))
        diagnostics.append(
            _make_error(
                line_idx,
                col_start,
                col_start + len("zMeta"),
                "zMeta is a root-level block — one per .zolo file, at indent 0. "
                "Nested here it is silently accepted at runtime but gets none of "
                "a root zMeta's real handling (it falls through as a plain nested "
                "key). Move this zMeta: block to the top of the file.",
            )
        )

    return diagnostics
