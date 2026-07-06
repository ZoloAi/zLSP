"""
Menu Option Validator — zLSP diagnostic for mismatched menu options

Validates that items declared in a menu options list have a corresponding
key in the expected scope, after stripping modifiers (^, ~, !, *).

Two forms are handled:

  Shorthand  — ~key*: [Option_A, ^Option_B, Option_C!]
               Options reference SIBLING keys at the same indent level.

  Longhand   — zMenu:
                   options: [Option_A, Option_B]
                   Option_A:
                       ...
               Options reference CHILD keys of the zMenu: block
               (meta-keys title, zAnchor, options, _zClass… are excluded).

Emits DiagnosticSeverity.Warning — mismatch is suspicious but may be
intentional (future key, dynamic injection), so we warn rather than error.
"""

import re
from typing import List

from lsprotocol import types as lsp_types


# ── constants ────────────────────────────────────────────────────────────────

# Known meta-keys inside a longhand zMenu: block that are NOT option entries
_ZMENU_META_KEYS = frozenset(
    {"title", "zAnchor", "options", "_zClass", "zGate", "zRBAC", "zMeta"}
)

# Modifier characters used on keys and option items
_PREFIX_CHARS = set("^~")
_SUFFIX_CHARS = set("*!")

# Matches an inline list value:  [item1, item2, item3]
_INLINE_LIST_RE = re.compile(r"^\[(.+)\]$")

# Matches a key line (indent + key + colon)
_KEY_LINE_RE = re.compile(r"^(\s*)([\^~]*)([A-Za-z_][A-Za-z0-9_\-]*)([*!]*)(\s*:.*)$")


# ── helpers ──────────────────────────────────────────────────────────────────

def _strip_modifiers(name: str) -> str:
    """Return the core name with all leading ^~ and trailing *! stripped."""
    core = name.strip()
    while core and core[0] in _PREFIX_CHARS:
        core = core[1:]
    while core and core[-1] in _SUFFIX_CHARS:
        core = core[:-1]
    return core


def _parse_inline_list(raw: str) -> List[str]:
    """Parse '[A, ^B, C!]' → ['A', '^B', 'C!']."""
    m = _INLINE_LIST_RE.match(raw.strip())
    if not m:
        return []
    return [item.strip() for item in m.group(1).split(",") if item.strip()]


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


def _make_warning(line_no: int, col_start: int, col_end: int, msg: str) -> lsp_types.Diagnostic:
    return lsp_types.Diagnostic(
        range=lsp_types.Range(
            start=lsp_types.Position(line=line_no, character=col_start),
            end=lsp_types.Position(line=line_no, character=col_end),
        ),
        message=msg,
        severity=lsp_types.DiagnosticSeverity.Warning,
        source="zolo-lsp",
    )


# ── main entry ───────────────────────────────────────────────────────────────

def validate_menu_options(content: str) -> List[lsp_types.Diagnostic]:
    """
    Scan .zolo content for menu option/key mismatches.

    Returns a list of Warning diagnostics (may be empty).
    """
    lines = content.splitlines()
    diagnostics: List[lsp_types.Diagnostic] = []

    for line_idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # ── Case 1: shorthand  ~key*: [...]  or  key*: [...]  ──────────────
        #   The key ends with * (possibly prefixed with ~) and value is [...]
        shorthand_match = re.match(
            r"^(\s*)([\^~]*)([A-Za-z_][A-Za-z0-9_\-]*)\*([!]*)\s*:\s*(\[.+\])\s*$",
            line,
        )
        if shorthand_match:
            menu_indent = _indent_level(line)
            options_raw = shorthand_match.group(5)
            options = _parse_inline_list(options_raw)
            if not options:
                continue

            # Collect sibling keys: same indent, within the same parent block.
            # Siblings end when we see a line at strictly less indent (parent closes).
            sibling_cores: set = set()
            for other_idx, other_line in enumerate(lines):
                if other_idx == line_idx:
                    continue
                if not other_line.strip() or other_line.strip().startswith("#"):
                    continue
                other_indent = _indent_level(other_line)
                if other_indent < menu_indent:
                    # Parent scope — stop collecting (siblings are bounded by parent)
                    # We do a full-file pass but filter by indent equality only
                    continue
                if other_indent == menu_indent:
                    km = re.match(
                        r"^\s*([\^~]*)([A-Za-z_][A-Za-z0-9_\-]*)([*!]*)\s*:",
                        other_line,
                    )
                    if km:
                        sibling_cores.add(km.group(2))  # core name

            # Validate each option
            # Find the character position of the opening [ on the menu line
            bracket_col = line.index("[")
            for option in options:
                core = _strip_modifiers(option)
                if core and core not in sibling_cores:
                    col = bracket_col
                    diagnostics.append(
                        _make_warning(
                            line_idx,
                            col,
                            col + len(options_raw),
                            f"Menu option '{option}' has no matching sibling key "
                            f"(expected a key named '{core}' at the same indent level).",
                        )
                    )
            continue

        # ── Case 2: longhand  zMenu:  block with  options: [...]  ──────────
        #   Detect "options: [...]" inside a zMenu: block and validate against
        #   the other child keys of that same zMenu: block.
        options_match = re.match(
            r"^(\s*)options\s*:\s*(\[.+\])\s*$",
            line,
        )
        if options_match:
            options_indent = _indent_level(line)
            options_raw = options_match.group(2)
            options = _parse_inline_list(options_raw)
            if not options:
                continue

            # Confirm we're inside a zMenu: block:
            # search backwards for the nearest "zMenu:" key at indent < options_indent
            parent_is_zmenu = False
            for prev_idx in range(line_idx - 1, -1, -1):
                prev_line = lines[prev_idx]
                if not prev_line.strip():
                    continue
                prev_indent = _indent_level(prev_line)
                if prev_indent < options_indent:
                    pm = re.match(r"^\s*zMenu\s*:", prev_line)
                    if pm:
                        parent_is_zmenu = True
                    break

            if not parent_is_zmenu:
                continue

            # Collect child keys of this zMenu: block (same indent as options:,
            # excluding known meta-keys)
            child_cores: set = set()
            for other_idx, other_line in enumerate(lines):
                if other_idx == line_idx:
                    continue
                if not other_line.strip() or other_line.strip().startswith("#"):
                    continue
                other_indent = _indent_level(other_line)
                if other_indent != options_indent:
                    continue
                km = re.match(
                    r"^\s*([\^~]*)([A-Za-z_][A-Za-z0-9_\-]*)([*!]*)\s*:",
                    other_line,
                )
                if km:
                    core_name = km.group(2)
                    if core_name not in _ZMENU_META_KEYS:
                        child_cores.add(core_name)

            # Validate each option
            bracket_col = line.index("[")
            for option in options:
                core = _strip_modifiers(option)
                if core and core not in child_cores:
                    col = bracket_col
                    diagnostics.append(
                        _make_warning(
                            line_idx,
                            col,
                            col + len(options_raw),
                            f"Menu option '{option}' has no matching child key in "
                            f"this zMenu block "
                            f"(expected a key named '{core}' as a sibling of 'options:').",
                        )
                    )

    return diagnostics
