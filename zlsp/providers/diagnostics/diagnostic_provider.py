"""
Diagnostics Engine for .zolo Language Server (Thin Wrapper)

Converts parse errors and validation issues into LSP diagnostics.

This is a THIN WRAPPER that delegates to DiagnosticFormatter.
All logic is in provider_modules/diagnostic_formatter.py for modularity.
"""

from typing import List, Optional
from lsprotocol import types as lsp_types

from zlsp.parser.parser_service import tokenize
from zlsp.exceptions import ZoloParseError
from .formatter import DiagnosticFormatter
from .menu_validators import validate_menu_options
from ..shared.value_validators import ValueValidator


def get_diagnostics(
    content: str,
    filename: Optional[str] = None
) -> List[lsp_types.Diagnostic]:
    """
    Parse .zolo content and return diagnostics (thin wrapper).
    
    Converts parse errors and validation issues into LSP diagnostic format.
    
    Args:
        content: Raw .zolo file content
        filename: Optional filename for context-aware diagnostics
    
    Returns:
        List of LSP diagnostics
    
    Implementation:
        This function is a thin wrapper that:
        1. Calls tokenize() to parse content
        2. Delegates error conversion to DiagnosticFormatter
        3. Returns LSP diagnostics
    
    All diagnostic formatting logic is in provider_modules/diagnostic_formatter.py.
    Zero duplication!
    """
    diagnostics = []

    try:
        # Parse content with filename for context-aware validation
        result = tokenize(content, filename=filename)

        # Convert string-based errors (legacy) using DiagnosticFormatter
        for error in result.errors:
            diagnostic = DiagnosticFormatter.from_error_message(error, content)
            diagnostics.append(diagnostic)

        # Convert structured diagnostics from parser (new)
        for diag in result.diagnostics:
            lsp_diagnostic = DiagnosticFormatter.from_internal_diagnostic(diag)
            diagnostics.append(lsp_diagnostic)

    except ZoloParseError as e:
        # Handle parse errors that weren't caught by tokenize()
        diagnostic = DiagnosticFormatter.from_error_message(str(e), content)
        diagnostics.append(diagnostic)

    except Exception as e:
        # Catch-all for unexpected errors
        diagnostic = DiagnosticFormatter.create_unexpected_error(e)
        diagnostics.append(diagnostic)

    return diagnostics


def validate_document(content: str) -> List[lsp_types.Diagnostic]:
    """
    Validate a .zolo document for style issues (thin wrapper).
    
    This goes beyond parsing to check for:
    - Style issues (e.g., trailing whitespace)
    - Best practices (TODO)
    - Potential problems (TODO)
    
    Args:
        content: Raw .zolo file content
    
    Returns:
        List of diagnostics (warnings and hints)
    
    Implementation:
        Delegates to DiagnosticFormatter.validate_style()
    """
    return DiagnosticFormatter.validate_style(content)


def get_all_diagnostics(
    content: str,
    include_style: bool = True,
    filename: Optional[str] = None
) -> List[lsp_types.Diagnostic]:
    """
    Get all diagnostics for a document (errors + optional style warnings + value validation).
    
    Args:
        content: Raw .zolo file content
        include_style: Whether to include style/linter warnings
        filename: Optional filename for context-aware diagnostics
    
    Returns:
        Combined list of all diagnostics
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("🔍 get_all_diagnostics called with filename=%s", filename)

    diagnostics = get_diagnostics(content, filename=filename)
    logger.info("   📋 Parse diagnostics: %d", len(diagnostics))

    if include_style:
        style_diags = validate_document(content)
        logger.info("   📋 Style diagnostics: %d", len(style_diags))
        diagnostics.extend(style_diags)

    # Add value validation (e.g., browser values in zConfig files)
    logger.info("   🔍 Calling ValueValidator.validate_document(filename=%s)", filename)
    value_diags = ValueValidator.validate_document(content, filename=filename)
    logger.info("   📋 Value diagnostics: %d", len(value_diags))
    diagnostics.extend(value_diags)

    # Add menu option/key mismatch validation
    menu_diags = validate_menu_options(content)
    logger.info("   📋 Menu diagnostics: %d", len(menu_diags))
    diagnostics.extend(menu_diags)

    logger.info("   ✅ Total diagnostics: %d", len(diagnostics))
    return diagnostics
