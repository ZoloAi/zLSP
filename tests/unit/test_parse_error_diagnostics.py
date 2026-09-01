"""
tokenize must surface fatal ZoloParseErrors as Error diagnostics.

Before 1.2.2 both tokenize paths caught ZoloParseError into the legacy
``errors`` list and returned data=None with ZERO diagnostics — the editor
underlined nothing for exactly the fault class strict boot (zOS#84) is about.
loads() keeps raising; tokenize now reports the same fault at its line.
"""

import pytest

from zlsp.exceptions import ZoloParseError
from zlsp.parser import loads, tokenize


ZVAF_NAMED_DUP = """Main:
    Card:
        zText: one
    Card:
        zText: two
"""

GENERIC_DUP = """cfg:
    port: 1
    port: 2
"""

SHORTHAND_REPEAT = """Main:
    zText: one
    zText: two
"""


class TestParseErrorDiagnostics:
    def test_zvaf_named_duplicate_emits_error_diagnostic(self):
        result = tokenize(ZVAF_NAMED_DUP, "zUI.test.zolo")
        assert result.data is None
        errors = [d for d in result.diagnostics if d.severity == 1]
        assert len(errors) == 1
        assert "Duplicate key 'Card'" in errors[0].message
        # message says "at line 3" (1-based) → diagnostic line 2 (0-based)
        assert errors[0].range.start.line == 2

    def test_generic_duplicate_emits_error_diagnostic(self):
        result = tokenize(GENERIC_DUP, "settings.zolo")
        assert result.data is None
        errors = [d for d in result.diagnostics if d.severity == 1]
        assert len(errors) == 1
        assert "Duplicate key 'port'" in errors[0].message

    def test_shorthand_repeat_is_supported_grammar_no_diagnostic(self):
        result = tokenize(SHORTHAND_REPEAT, "zUI.test.zolo")
        assert result.diagnostics == []
        assert list(result.data["Main"].keys()) == ["zText", "zText__dup2"]

    def test_loads_still_raises(self):
        with pytest.raises(ZoloParseError):
            loads(ZVAF_NAMED_DUP, filename="zUI.test.zolo")

    def test_clean_file_no_diagnostics(self):
        result = tokenize("Main:\n    zText: hello\n", "zUI.test.zolo")
        assert result.diagnostics == []
        assert result.data == {"Main": {"zText": "hello"}}
