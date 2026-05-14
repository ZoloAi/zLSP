"""
Parser Service - Early File Type Detection & Routing

Routes parsing requests to appropriate parser based on file type.
Detects file type BEFORE parsing to avoid zvaf overhead for basic files.

Architecture:
- BASIC: Core + Basic (JSON/YAML features) - No zvaf imports
- ZVAF: Core + Basic + zVaF (UI extensions, modifiers, etc.)

This is the EARLIEST detection point - happens at server entry, not inside parser.
"""

from typing import Optional
from zlsp.lsp_types import ParseResult
from .zvaf.file_type_detector import FileTypeDetector, FileType


class ParserService:
    """
    Parser router that detects file type and delegates to appropriate parser.
    
    This is the ENTRY POINT for all parsing operations (LSP and runtime).
    File type detection happens HERE - before any parser code runs.
    """

    @staticmethod
    def tokenize(content: str, filename: Optional[str] = None) -> ParseResult:
        """
        Parse .zolo content with semantic tokens (LSP path).
        
        Detects file type and routes to:
        - Basic tokenizer: For generic .zolo files
        - zVaF tokenizer: For zUI/zEnv/zSpark/zConfig/zSchema files
        
        Args:
            content: Raw .zolo file content
            filename: Optional filename for file type detection
            
        Returns:
            ParseResult with data, tokens, diagnostics
        """
        # EARLIEST DETECTION - Detect file type before any parsing
        file_type = FileTypeDetector(filename).file_type

        if file_type == FileType.GENERIC:
            # Basic path - NO zvaf code touched
            from .parser import tokenize_basic
            return tokenize_basic(content, filename)
        else:
            # zVaF path - Full extensions enabled
            from .parser import tokenize_zvaf
            return tokenize_zvaf(content, filename)

    @staticmethod
    def loads(content: str, filename: Optional[str] = None) -> any:
        """
        Parse .zolo content (runtime path - no tokens).
        
        Detects file type and routes to:
        - Basic parser: For generic .zolo files
        - zVaF parser: For zUI/zEnv/zSpark/zConfig/zSchema files
        
        Args:
            content: Raw .zolo file content
            filename: Optional filename for file type detection
            
        Returns:
            Parsed data (dict, list, or scalar)
        """
        # EARLIEST DETECTION - Detect file type before any parsing
        file_type = FileTypeDetector(filename).file_type

        if file_type == FileType.GENERIC:
            # Basic path - NO zvaf code touched
            from .parser import loads_basic
            return loads_basic(content)
        else:
            # zVaF path - Full extensions enabled
            from .parser import loads_zvaf
            return loads_zvaf(content)


# Convenience exports for backward compatibility
def tokenize(content: str, filename: Optional[str] = None) -> ParseResult:
    """Parse with tokens (LSP) - routes based on file type."""
    return ParserService.tokenize(content, filename)


def loads(content: str, filename: Optional[str] = None) -> any:
    """Parse without tokens (runtime) - routes based on file type."""
    return ParserService.loads(content, filename)
