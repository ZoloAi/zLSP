"""
Completion Provider for .zolo Language Server (Thin Wrapper + Router)

Provides smart autocomplete for:
- Type hints when typing inside () (from DocumentationRegistry)
- Common values (true, false, null) (from DocumentationRegistry)
- File-type-specific completions (zSpark, zUI, zSchema)
- Context-aware suggestions

Phase 3 Architecture:
This wrapper now routes to specialized providers based on file type:
- Generic .zolo → BasicCompletionProvider (fast, lightweight)
- zVAF files → ZVAFCompletionProvider (full features)

Benefits:
- Basic files skip zVAF overhead (faster)
- Clear separation of concerns
- Independent evolution of basic vs zVAF features
"""

from typing import List, Optional
from lsprotocol import types as lsp_types
from .completion_router import CompletionRouter


def get_completions(
    content: str,
    line: int,
    character: int,
    filename: Optional[str] = None
) -> List[lsp_types.CompletionItem]:
    """
    Get completion items at a specific position (routes to appropriate provider).
    
    Phase 3 Architecture:
    Routes completion requests based on file type:
    1. Generic .zolo files → BasicCompletionProvider
       - Type hints inside ()
       - Common values (true, false, null)
       - No theme loading, no file-type detection overhead
    
    2. zVAF files (zSpark, zUI, zEnv, zConfig, zSchema) → ZVAFCompletionProvider
       - All basic features
       - File-type-specific key completions from theme
       - File-type + key specific value completions
       - UI element completions
       - Block key detection
       - Parent key context analysis
    
    Args:
        content: Full .zolo file content
        line: Line number (0-based)
        character: Character position (0-based)
        filename: Optional filename for file-type detection and routing
    
    Returns:
        List of completion items from appropriate provider
    
    Implementation:
        1. CompletionRouter.route() detects file type
        2. Routes to BasicCompletionProvider or ZVAFCompletionProvider
        3. Returns context-aware completion items
    
    All completion logic is now split between:
    - providers/basic/basic_completion_provider.py (core features)
    - providers/zvaf/zvaf_completion_provider.py (zVAF features)
    - providers/shared/ (SSOT: documentation, classifications)
    - themes/zolo_default.yaml (SSOT: key and value completions)
    """
    # Route to appropriate provider based on file type
    return CompletionRouter.route(content, line, character, filename)
