"""
Completion Router - Routes completion requests to Basic or zVAF providers

This is the routing layer that determines which completion provider to use
based on file type detection:

- Generic .zolo files → BasicCompletionProvider (fast, lightweight)
- zVAF files (zSpark, zUI, zEnv, zConfig, zSchema) → ZVAFCompletionProvider (full features)

Architecture:
┌─────────────────────────────────────┐
│    completion_router.py             │
│    CompletionRouter.route()         │
└──────────────┬──────────────────────┘
               │
               ├─ detect_file_type()
               │
        ┌──────┴───────┐
        │              │
        ▼              ▼
┌──────────────┐  ┌────────────────┐
│ GENERIC      │  │ zVAF           │
│ FileType     │  │ FileType       │
└──────┬───────┘  └─────┬──────────┘
       │                │
       ▼                ▼
┌──────────────┐  ┌────────────────┐
│ Basic        │  │ zVAF           │
│ Provider     │  │ Provider       │
└──────────────┘  └────────────────┘

Benefits:
- Basic files skip zVAF overhead (faster)
- Clear separation of concerns
- Independent evolution of basic vs zVAF features
- Easier testing and maintenance
"""

from typing import List, Optional
from lsprotocol import types as lsp_types

from zlsp.parser.zvaf.file_type_detector import FileType, detect_file_type
from ..basic import BasicCompletionProvider
from ..zvaf import ZVAFCompletionProvider


class CompletionRouter:
    """
    Routes completion requests to the appropriate provider.
    
    Analyzes file type and delegates to:
    - BasicCompletionProvider for generic .zolo files
    - ZVAFCompletionProvider for zVAF files (zSpark, zUI, etc.)
    """
    
    @staticmethod
    def route(
        content: str,
        line: int,
        character: int,
        filename: Optional[str] = None
    ) -> List[lsp_types.CompletionItem]:
        """
        Route completion request to appropriate provider.
        
        Args:
            content: Full .zolo file content
            line: Line number (0-based)
            character: Character position (0-based)
            filename: Optional filename for file type detection
        
        Returns:
            List of completion items from appropriate provider
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Detect file type
        file_type = detect_file_type(filename) if filename else FileType.GENERIC
        
        logger.info("━" * 60)
        logger.info("🔀 CompletionRouter")
        logger.info("   File: %s", filename or "(no filename)")
        logger.info("   Detected type: %s", file_type)
        logger.info("   Position: line=%s, char=%s", line, character)
        
        # Route based on file type
        if file_type == FileType.GENERIC:
            # Generic .zolo file → Use basic provider
            logger.info("   ✅ Routing to → BasicCompletionProvider (fast path)")
            logger.info("━" * 60)
            return BasicCompletionProvider.get_completions(content, line, character)
        else:
            # zVAF file → Use full zVAF provider
            logger.info("   ✅ Routing to → ZVAFCompletionProvider (full features)")
            logger.info("   File type: %s", file_type.value)
            logger.info("━" * 60)
            
            # zVAF provider requires filename for context
            if not filename:
                logger.warning("   ⚠️  zVAF file detected but no filename provided")
                # Fallback to basic completions
                return BasicCompletionProvider.get_completions(content, line, character)
            
            return ZVAFCompletionProvider.get_completions(
                content, line, character, filename
            )
