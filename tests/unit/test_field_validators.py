"""
Unit tests for zDialog field block-mapping validator.

`.zolo` is string-first, not YAML. A `- key: value` block-mapping list item
under a zDialog `fields:` block is silently mis-parsed, so the LSP flags it as
an Error and steers the author to the inline `[{}]` form.
"""

from lsprotocol import types as lsp_types

from zlsp.providers.diagnostics.field_validators import validate_dialog_fields


class TestValidateDialogFields:
    """Direct tests of validate_dialog_fields()."""

    def test_block_mapping_field_is_flagged(self):
        content = "\n".join([
            "Form:",
            "    zDialog:",
            "        fields:",
            "            - name",
            "            - name: age",
            "              type: number",
        ])
        diags = validate_dialog_fields(content)
        assert len(diags) == 1
        d = diags[0]
        assert d.severity == lsp_types.DiagnosticSeverity.Error
        assert d.range.start.line == 4  # the "- name: age" opener
        assert "inline form" in d.message

    def test_inline_flow_dicts_are_ok(self):
        content = "\n".join([
            "Form:",
            "    zDialog:",
            "        fields:",
            "            - name",
            "            - {name: age, type: number}",
            "            - {name: email, type: email}",
        ])
        assert validate_dialog_fields(content) == []

    def test_bare_names_are_ok(self):
        content = "\n".join([
            "Form:",
            "    zDialog:",
            "        fields:",
            "            - name",
            "            - email",
            "            - password",
        ])
        assert validate_dialog_fields(content) == []

    def test_multiple_block_fields_each_flagged(self):
        content = "\n".join([
            "Form:",
            "    zDialog:",
            "        fields:",
            "            - name: age",
            "              type: number",
            "            - name: phone",
            "              type: tel",
        ])
        diags = validate_dialog_fields(content)
        assert len(diags) == 2
        assert {d.range.start.line for d in diags} == {3, 5}

    def test_inline_fields_list_is_ok(self):
        # Whole list on the `fields:` line — not a block, never scanned.
        content = "\n".join([
            "Form:",
            "    zDialog:",
            "        fields: [name, {name: age, type: number}]",
        ])
        assert validate_dialog_fields(content) == []

    def test_block_mapping_outside_zdialog_is_ignored(self):
        # `-` block mapping is valid elsewhere; only zDialog fields are scoped.
        content = "\n".join([
            "models:",
            "    fields:",
            "        - name: age",
            "          type: number",
        ])
        assert validate_dialog_fields(content) == []

    def test_block_ends_at_dedent(self):
        # A sibling key after the block must not be scanned as a field item.
        content = "\n".join([
            "Form:",
            "    zDialog:",
            "        fields:",
            "            - name",
            "        onSubmit:",
            "            zFunc: &demo.hello()",
        ])
        assert validate_dialog_fields(content) == []
