"""Comment-pairing diagnostics (zOS#80 / zOS#106).

The #> swallow is silent and non-local: an unclosed opener eats everything
until the next <# anywhere below, and when the span crosses an ignore: list
the exclusion list fails OPEN (the zOS#106 field leak shipped a private
financial model this way). The tokenize path must warn on both anomaly
shapes; well-formed comments must stay diagnostic-free.
"""
from zlsp.parser.parser import tokenize_basic


def _pairing_warnings(result):
    return [d for d in result.diagnostics if "#>" in d.message or "<#" in d.message]


def test_wellformed_comments_no_diagnostics():
    content = (
        "# plain line comment\n"
        "#> closed single-line <#\n"
        "key: value\n"
        "#> a multi-line\n"
        "comment body <#\n"
        "other: thing\n"
    )
    result = tokenize_basic(content)
    assert _pairing_warnings(result) == []


def test_unterminated_opener_warns():
    content = "key: value\n#> never closed\nother: thing\n"
    result = tokenize_basic(content)
    warnings = _pairing_warnings(result)
    assert len(warnings) == 1
    assert "Unterminated" in warnings[0].message
    assert warnings[0].severity == 2
    assert warnings[0].range.start.line == 1  # 0-based: the #> line


def test_leak_shape_inner_opener_warns():
    # The zOS#106 shape: opener 1 unclosed; comment 2's <# closes it, so the
    # entries between are swallowed. The warning lands on the INNER #>.
    content = (
        "zProject:\n"
        "    ignore: [\n"
        "        #> keep the private stuff out\n"
        "        Source Data/*,\n"
        "        NOTES.md,\n"
        "        #> note for Gal <#\n"
        "        NOTE-*.txt\n"
        "    ]\n"
    )
    result = tokenize_basic(content)
    warnings = _pairing_warnings(result)
    assert len(warnings) == 1
    assert "line 3" in warnings[0].message  # names the stale opener (1-based)
    assert warnings[0].range.start.line == 5  # 0-based: the inner #> line
    assert warnings[0].severity == 2


def test_literal_hash_untouched():
    # Bare # in values (hex colors) must not trigger anything.
    content = "color: #ff8800\nlabel: use #> to comment  # trailing note\n"
    result = tokenize_basic(content)
    # the lone `#>` in prose IS an unterminated opener — that's the point:
    # the runtime would swallow from there. One warning expected, no crash.
    assert len(_pairing_warnings(result)) == 1
