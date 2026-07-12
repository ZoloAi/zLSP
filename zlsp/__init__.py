"""
zlsp - Zolo Language Server Protocol

This package provides LSP support for .zolo files.
"""

from pathlib import Path

from .version import __version__

# Main submodules available for import
__all__ = [
    "parser", 
    "cli", 
    "server", 
    "providers", 
    "lsp_types", 
    "token_types",
    "token_registry",
    "exceptions", 
    "version",
    "bifrost_prism_dir",
]


def bifrost_prism_dir() -> Path:
    """Path to the pre-built Prism.js syntax bundle shipped as package data.

    Contract consumed by zOS.zServer (mounted read-only at /zsyntax/<version>/):
    the directory contains prism-zolo.js, prism-{zspark,zui,zschema,zconfig,
    zenv}.js and prism-zolo-theme.css. The bundle is generated at build time
    (zlsp/generators, see SSOT_PRISM_GENERATION.md) — never at runtime — so it
    always matches THIS package's grammar version.

    Raises FileNotFoundError if the bundle is missing (broken install), so a
    caller can distinguish "old zlsp, no accessor" (AttributeError) from
    "new zlsp, damaged package".
    """
    bundle = Path(__file__).parent / "generated"
    if not (bundle / "prism-zolo.js").is_file():
        raise FileNotFoundError(f"prism bundle missing from install: {bundle}")
    return bundle
