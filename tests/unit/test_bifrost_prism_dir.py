"""Contract test for the zOS.zServer prism-bundle accessor.

zServer mounts bifrost_prism_dir() read-only at /zsyntax/<version>/ and the
bifrost client loads these exact filenames — a missing file here means broken
highlighting in every deployed app on the next zolo-lsp upgrade.
"""

import zlsp

_CONTRACT_FILES = (
    "prism-zolo.js",
    "prism-zspark.js",
    "prism-zui.js",
    "prism-zschema.js",
    "prism-zconfig.js",
    "prism-zenv.js",
    "prism-zolo-theme.css",
)


def test_bifrost_prism_dir_returns_complete_bundle():
    bundle = zlsp.bifrost_prism_dir()
    assert bundle.is_dir()
    missing = [name for name in _CONTRACT_FILES if not (bundle / name).is_file()]
    assert not missing, f"prism bundle incomplete: {missing}"


def test_bundle_files_are_nonempty():
    bundle = zlsp.bifrost_prism_dir()
    empty = [name for name in _CONTRACT_FILES if (bundle / name).stat().st_size == 0]
    assert not empty, f"empty bundle files: {empty}"
