"""
Quoted-value validators for .zolo files.

zolo is string-first: values do NOT need quotes.
This validator detects common cases where the LLM (or human) unnecessarily wraps
values in double-quotes, which can cause silent parse failures in zFunc.

Hardcoded targets (repeated offenders):
  zFunc   — wrapping in " " causes bracket-mismatch at runtime
  content — wrapping "..." prevents zHat token substitution in zText/zMD

A WARNING is emitted (not ERROR) so the file still parses; the IDE overlay
immediately signals the mistake before the user runs the app.
"""

import re
from typing import List

from lsprotocol import types as lsp_types


# Keys where a quoted value is always wrong in zolo (string-first)
_QUOTED_VALUE_KEYS = {
    "zFunc",
    "content",
    "label",
    "prompt",
    "placeholder",
    "title",
}

# Regex: key followed by optional spaces, colon, optional space, then " or '
_QUOTED_LINE_RE = re.compile(
    r'^(?P<indent>\s*)(?P<key>\w+)\s*:\s*(?P<quote>["\'])(?P<inner>.*?)(?P=quote)\s*$'
)


def validate_quoted_values(content: str) -> List[lsp_types.Diagnostic]:
    """
    Scan a .zolo file and warn on needlessly quoted values.

    Targets: keys in _QUOTED_VALUE_KEYS where the entire RHS is wrapped in " or '.

    Returns a WARNING diagnostic pointing at the opening quote character.
    """
    diagnostics: List[lsp_types.Diagnostic] = []
    lines = content.splitlines()

    for line_idx, line in enumerate(lines):
        m = _QUOTED_LINE_RE.match(line)
        if not m:
            continue

        key = m.group("key")
        if key not in _QUOTED_VALUE_KEYS:
            continue

        quote_char = m.group("quote")
        inner = m.group("inner")
        indent_len = len(m.group("indent"))

        # Calculate column of the opening quote
        # "indent + key + : + optional_space" until quote
        colon_idx = line.index(":", indent_len)
        quote_col = line.index(quote_char, colon_idx)

        # Build helpful message
        if key == "zFunc":
            msg = (
                f'zFunc value is quoted — remove the outer {quote_char!r}. '
                f"zolo is string-first: quotes around function calls cause a "
                f"bracket-mismatch parse error at runtime.\n"
                f"  Fix: zFunc: {inner}"
            )
            severity = lsp_types.DiagnosticSeverity.Error
        else:
            msg = (
                f'{key} value is unnecessarily quoted — zolo is string-first. '
                f"Remove the outer {quote_char!r} unless the value contains "
                f"':', '#', or starts with '['.\n"
                f"  Fix: {key}: {inner}"
            )
            severity = lsp_types.DiagnosticSeverity.Warning

        diagnostics.append(
            lsp_types.Diagnostic(
                range=lsp_types.Range(
                    start=lsp_types.Position(line=line_idx, character=quote_col),
                    end=lsp_types.Position(
                        line=line_idx,
                        character=len(line.rstrip()),
                    ),
                ),
                message=msg,
                severity=severity,
                source="zLSP",
                code="zolo-quoted-value",
            )
        )

    return diagnostics
