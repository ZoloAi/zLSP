"""
Zolo Parser - Public API and Orchestration

Main parser module with public API (load, loads, dump, dumps, tokenize).
All implementation delegated to modular components in parser_modules/.

This file is THIN - it only orchestrates, doesn't implement.
"""

from pathlib import Path
from typing import Any, Union, Optional, IO

# Import exceptions
from zlsp.exceptions import ZoloParseError, ZoloDumpError

# Import types
from zlsp.lsp_types import ParseResult

# Import from modular components
from .core import (
    TokenEmitter,
    check_indentation_consistency,
    parse_lines_with_tokens,
)
from .zvaf import parse_lines_zvaf, FileTypeDetector
from .basic import (
    process_type_hints,
    strip_comments_and_prepare_lines,
    strip_comments_and_prepare_lines_with_tokens,
    serialize_zolo,
)

# Import constants
from .constants import FILE_EXT_ZOLO


# ============================================================================
# PUBLIC API - Entry points for users
# ============================================================================
# NOTE: Main entry points are in parser_service.py (tokenize/loads with routing)
# These functions are internal implementations called by the service layer.

def tokenize_basic(content: str, filename: Optional[str] = None) -> ParseResult:
    """
    Parse BASIC .zolo content with semantic tokens (Core + Basic only, NO zvaf).
    
    Used for generic .zolo files that don't need zVaF extensions.
    Faster than tokenize_zvaf() - no modifier handling, no UI shorthands.
    
    Args:
        content: Raw .zolo file content
        filename: Optional filename (for context)
        
    Returns:
        ParseResult with data, tokens, and any errors
    """
    # Create emitter with NO zvaf flags (all False)
    emitter = TokenEmitter(
        content,
        filename=filename,
        is_zui_file=False,
        is_zenv_file=False,
        is_zspark_file=False,
        is_zconfig_file=False,
        is_zschema_file=False,
        zui_component_name=None,
        zspark_component_name=None,
        zconfig_component_name=None
    )
    errors = []

    try:
        # Parse with BASIC tokenization (no zvaf extensions)
        data = _parse_basic_content_with_tokens(content, emitter)
        return ParseResult(
            data=data,
            tokens=emitter.get_tokens(),
            errors=errors,
            diagnostics=emitter.diagnostics
        )
    except ZoloParseError as e:
        # Still return tokens even if parse failed
        errors.append(str(e))
        return ParseResult(
            data=None,
            tokens=emitter.get_tokens(),
            errors=errors,
            diagnostics=emitter.diagnostics
        )


def tokenize_zvaf(content: str, filename: Optional[str] = None) -> ParseResult:
    """
    Parse ZVAF .zolo content with semantic tokens (Core + Basic + zVaF).
    
    Used for zUI/zEnv/zSpark/zConfig/zSchema files with full zVaF extensions.
    Includes modifiers, UI shorthands, auto-multiline, etc.
    
    Args:
        content: Raw .zolo file content
        filename: Optional filename for context-aware tokenization (e.g., zUI files)

    Returns:
        ParseResult with data, tokens, and any errors
    """
    # Detect file type (zVaF layer responsibility)
    file_detector = FileTypeDetector(filename)

    # Create emitter with detected file type info (decoupled from zvaf)
    emitter = TokenEmitter(
        content,
        filename=filename,
        is_zui_file=file_detector.is_zui() or file_detector.is_zraven(),
        is_zenv_file=file_detector.is_zenv(),
        is_zspark_file=file_detector.is_zspark(),
        is_zconfig_file=file_detector.is_zconfig(),
        is_zschema_file=file_detector.is_zschema(),
        zui_component_name=file_detector.component_name if (file_detector.is_zui() or file_detector.is_zraven()) else None,
        zspark_component_name=file_detector.component_name if file_detector.is_zspark() else None,
        zconfig_component_name=file_detector.component_name if file_detector.is_zconfig() else None
    )
    errors = []

    try:
        # Parse with ZVAF token emission (full extensions)
        data = _parse_zvaf_content_with_tokens(content, emitter)
        return ParseResult(
            data=data,
            tokens=emitter.get_tokens(),
            errors=errors,
            diagnostics=emitter.diagnostics
        )
    except ZoloParseError as e:
        # Still return tokens even if parse failed
        errors.append(str(e))
        return ParseResult(
            data=None,
            tokens=emitter.get_tokens(),
            errors=errors,
            diagnostics=emitter.diagnostics
        )


def load(fp: Union[str, Path, IO], file_extension: Optional[str] = None) -> Any:
    """
    Load data from a .zolo file.

    Args:
        fp: File path (str/Path) or file-like object
        file_extension: Optional file extension override
                       If None, will detect from file path or default to .zolo

    Returns:
        Parsed data (dict, list, or scalar)

    Raises:
        ZoloParseError: If parsing fails
        FileNotFoundError: If file doesn't exist

    Examples:
        >>> # Load .zolo file
        >>> data = zolo.load('config.zolo')

        >>> # Load with explicit extension
        >>> data = zolo.load('config.txt', file_extension='.zolo')
    """
    # Handle file path vs file-like object
    if isinstance(fp, (str, Path)):
        file_path = Path(fp)
        filename = file_path.name

        # Detect file extension if not provided
        if file_extension is None:
            file_extension = file_path.suffix.lower()
            if not file_extension:
                file_extension = FILE_EXT_ZOLO  # Default to .zolo

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"File not found: {file_path}") from exc
        except Exception as e:
            raise ZoloParseError(f"Error reading file {file_path}: {e}") from e
    else:
        # File-like object
        try:
            content = fp.read()
        except Exception as e:
            raise ZoloParseError(f"Error reading from file object: {e}") from e

        # Try to detect filename from file object
        filename = None
        if hasattr(fp, 'name'):
            filename = Path(fp.name).name
            file_extension = Path(fp.name).suffix.lower()
        if not file_extension:
            file_extension = FILE_EXT_ZOLO  # Default to .zolo

    # Parse content with filename for file type detection
    return loads(content, filename=filename)


def loads(s: str, filename: Optional[str] = None) -> Any:
    """
    Load data from .zolo string with automatic routing to BASIC or ZVAF parser.
    
    Routes to loads_zvaf() for zUI/zEnv/zSpark/zConfig/zSchema files.
    Routes to loads_basic() for generic .zolo files.
    
    Args:
        s: String content to parse
        filename: Optional filename for file type detection

    Returns:
        Parsed data (dict, list, or scalar)

    Raises:
        ZoloParseError: If parsing fails
    """
    # Detect file type for routing
    file_detector = FileTypeDetector(filename)

    # Route to appropriate parser
    if file_detector.needs_zvaf():
        return loads_zvaf(s)
    else:
        return loads_basic(s)


def loads_basic(s: str) -> Any:
    """
    Load data from BASIC .zolo string (Core + Basic only, NO zvaf).
    
    Used for generic .zolo files. Faster than loads_zvaf().
    
    Args:
        s: String content to parse

    Returns:
        Parsed data (dict, list, or scalar)

    Raises:
        ZoloParseError: If parsing fails
    """
    if not s or not s.strip():
        return None

    # .zolo files use RFC 8259 type detection
    string_first = False

    # Parse .zolo content with BASIC parser (no zvaf extensions)
    try:
        parsed = _parse_basic_content(s)

        # Process type hints
        parsed = process_type_hints(parsed, string_first=string_first)

        return parsed

    except ZoloParseError:
        raise  # Re-raise our own exceptions
    except Exception as e:
        raise ZoloParseError(f"Parsing error: {e}") from e


def loads_zvaf(s: str) -> Any:
    """
    Load data from ZVAF .zolo string (Core + Basic + zVaF).
    
    Used for zUI/zEnv/zSpark/zConfig/zSchema files with full zVaF extensions.

    Args:
        s: String content to parse

    Returns:
        Parsed data (dict, list, or scalar)

    Raises:
        ZoloParseError: If parsing fails
    """
    if not s or not s.strip():
        return None

    # .zolo files use RFC 8259 type detection
    string_first = False

    # Parse .zolo content with ZVAF parser (full extensions)
    try:
        parsed = _parse_zvaf_content(s)

        # Process type hints
        parsed = process_type_hints(parsed, string_first=string_first)

        return parsed

    except ZoloParseError:
        raise  # Re-raise our own exceptions
    except Exception as e:
        raise ZoloParseError(f"Parsing error: {e}") from e


def dump(
    data: Any,
    fp: Union[str, Path, IO],
    file_extension: Optional[str] = None,
    **kwargs
) -> None:
    """
    Dump data to a .zolo file.

    Args:
        data: Data to serialize (dict, list, or scalar)
        fp: File path (str/Path) or file-like object
        file_extension: Optional file extension override (reserved for future use)
        **kwargs: Reserved for future format options

    Raises:
        ZoloDumpError: If serialization fails

    Examples:
        >>> data = {'port': 8080, 'host': 'localhost'}
        >>> zolo.dump(data, 'config.zolo')
    """
    # Serialize to string
    content = dumps(data, _file_extension=file_extension, **kwargs)

    # Write to file
    if isinstance(fp, (str, Path)):
        file_path = Path(fp)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise ZoloDumpError(f"Error writing file {file_path}: {e}") from e
    else:
        # File-like object
        try:
            fp.write(content)
        except Exception as e:
            raise ZoloDumpError(f"Error writing to file object: {e}") from e


def dumps(data: Any, _file_extension: Optional[str] = None, **_kwargs) -> str:
    """
    Dump data to a .zolo string.

    Args:
        data: Data to serialize (dict, list, or scalar)
        file_extension: Optional file extension hint (reserved for future use)
        **kwargs: Reserved for future format options

    Returns:
        Serialized string

    Raises:
        ZoloDumpError: If serialization fails

    Examples:
        >>> data = {'port': 8080, 'host': 'localhost'}
        >>> zolo.dumps(data)
        'port: 8080\\nhost: localhost'
    """
    # Serialize as pure .zolo format
    try:
        return serialize_zolo(data)
    except ZoloDumpError:
        raise  # Re-raise our own exceptions
    except Exception as e:
        raise ZoloDumpError(f"Serialization error: {e}") from e


# ============================================================================
# PRIVATE ORCHESTRATION - Internal coordination functions
# ============================================================================

def _parse_basic_content(content: str) -> Any:
    """
    BASIC .zolo parser (Core + Basic only, NO zvaf extensions).
    
    Faster than _parse_zvaf_content() for generic .zolo files.
    
    Orchestrates the parsing pipeline:
    1. Strip comments and prepare lines
    2. Check indentation consistency
    3. Parse lines with BASIC parser (no auto-multiline, no UI shorthands)
    """
    from .core.line_parsers.standard_parser import parse_lines as parse_lines_basic

    # Step 1: Strip comments and prepare lines
    lines, line_mapping = strip_comments_and_prepare_lines(content)

    # Step 2: Check indentation consistency (Python-style)
    check_indentation_consistency(lines)

    # Step 3: Parse with BASIC parser (Core + Basic features only)
    result = parse_lines_basic(lines, line_mapping)

    return result


def _parse_zvaf_content(content: str) -> Any:
    """
    ZVAF .zolo parser (Core + Basic + zVaF extensions).
    
    Used for zUI/zEnv/zSpark/zConfig/zSchema files.

    Orchestrates the parsing pipeline:
    1. Strip comments and prepare lines
    2. Check indentation consistency
    3. Parse lines with zVaF extensions (auto-multiline, UI shorthands)
    """
    # Step 1: Strip comments and prepare lines
    lines, line_mapping = strip_comments_and_prepare_lines(content)

    # Step 2: Check indentation consistency (Python-style)
    check_indentation_consistency(lines)

    # Step 3: Parse with zVaF extensions (auto-multiline, UI shorthands)
    result = parse_lines_zvaf(lines, line_mapping)

    return result


def _parse_basic_content_with_tokens(content: str, emitter: TokenEmitter) -> Any:
    """
    BASIC .zolo parser with token emission (Core + Basic only, NO zvaf).
    
    Faster than _parse_zvaf_content_with_tokens() for generic .zolo files.

    Orchestrates the parsing pipeline with tokenization:
    1. Strip comments and prepare lines (emit comment tokens)
    2. Check indentation consistency
    3. Parse lines with BASIC token emission (no zvaf features)
    """
    # Step 1: Strip comments and prepare lines (with token emission)
    lines, line_mapping = strip_comments_and_prepare_lines_with_tokens(content, emitter)

    # Step 2: Check indentation consistency
    check_indentation_consistency(lines)

    # Step 3: Parse with BASIC token emission (Core + Basic only)
    # NOTE: parse_lines_with_tokens will detect is_zvaf=False from emitter flags
    result = parse_lines_with_tokens(lines, line_mapping, emitter)

    return result


def _parse_zvaf_content_with_tokens(content: str, emitter: TokenEmitter) -> Any:
    """
    ZVAF .zolo parser with token emission (Core + Basic + zVaF).
    
    Used for zUI/zEnv/zSpark/zConfig/zSchema files.

    This version tracks positions and emits semantic tokens during parsing.

    Orchestrates the parsing pipeline with tokenization:
    1. Strip comments and prepare lines (emit comment tokens)
    2. Check indentation consistency
    3. Parse lines with ZVAF token emission (full extensions)
    """
    # Step 1: Strip comments and prepare lines (with token emission)
    lines, line_mapping = strip_comments_and_prepare_lines_with_tokens(content, emitter)

    # Step 2: Check indentation consistency
    check_indentation_consistency(lines)

    # Step 3: Parse with ZVAF token emission (full extensions)
    # NOTE: parse_lines_with_tokens will detect is_zvaf=True from emitter flags
    result = parse_lines_with_tokens(lines, line_mapping, emitter)

    return result
