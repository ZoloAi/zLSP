"""
Unit tests for the zMeta root-position validator.

`zMeta` is a canonical ROOT-level block (indent 0). Nested inside another
block it is silently accepted by the runtime but gets none of a real root
zMeta's handling, so the LSP flags it as an Error.
"""

from lsprotocol import types as lsp_types

from zlsp.providers.diagnostics.meta_position_validators import validate_meta_position


class TestValidateMetaPosition:
    """Direct tests of validate_meta_position()."""

    def test_root_level_zmeta_is_ok(self):
        content = "\n".join([
            "zMeta:",
            "    zNavBar: false",
            "",
            "Main:",
            "    zH1:",
            "        label: Hello",
        ])
        assert validate_meta_position(content) == []

    def test_nested_zmeta_inside_block_is_flagged(self):
        content = "\n".join([
            "Main:",
            "    zMeta:",
            "        zBrush:   [ztasklist]",
            "        zScripts: [&.tasklist]",
            "",
            "    zH1:",
            "        label: Task List",
        ])
        diags = validate_meta_position(content)
        assert len(diags) == 1
        d = diags[0]
        assert d.severity == lsp_types.DiagnosticSeverity.Error
        assert d.range.start.line == 1  # the nested "zMeta:" line
        assert "root-level" in d.message

    def test_multiple_nested_zmeta_each_flagged(self):
        content = "\n".join([
            "Main:",
            "    zMeta:",
            "        zBrush: [a]",
            "",
            "Other:",
            "    zMeta:",
            "        zBrush: [b]",
        ])
        diags = validate_meta_position(content)
        assert len(diags) == 2
        assert {d.range.start.line for d in diags} == {1, 5}

    def test_zschema_root_zmeta_is_ok(self):
        content = "\n".join([
            "zMeta:",
            "    Data_Type: csv",
            "    Data_Label: Companies",
            "",
            "Companies:",
            "    id:",
            "        type: int",
        ])
        assert validate_meta_position(content) == []

    def test_dotted_zmeta_reference_is_not_flagged(self):
        # `zMeta.zSpool: [...]` on one line is a different key, not a block open.
        content = "\n".join([
            "Main:",
            "    zMeta.zSpool: [contacts]",
            "    zH1:",
            "        label: Hello",
        ])
        assert validate_meta_position(content) == []

    def test_zmeta_mentioned_in_value_is_not_flagged(self):
        content = "\n".join([
            "Main:",
            "    zMD:",
            "        content: See zMeta for details.",
        ])
        assert validate_meta_position(content) == []
