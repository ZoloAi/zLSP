"""
Basic Completion Provider - Generic .zolo file completions

Provides completions for core .zolo features that work in any .zolo file:
- Type hints inside parentheses: key(█) → int, float, bool, str...
- Common values after colon: key: █ → true, false, null
- Generic key-value patterns

This provider is fast and lightweight - no file-type detection,
no theme loading, no complex context analysis.

Used for: Generic .zolo files without zVAF extensions
"""

from typing import List, Optional
from lsprotocol import types as lsp_types

from ..shared.documentation_registry import DocumentationRegistry, DocumentationType


class BasicCompletionProvider:
    """
    Provides basic completions for generic .zolo files.
    
    Handles only core features that apply to all .zolo files.
    """
    
    @staticmethod
    def get_completions(
        content: str,
        line: int,
        character: int
    ) -> List[lsp_types.CompletionItem]:
        """
        Get completions for generic .zolo files.
        
        Args:
            content: Full .zolo file content
            line: Line number (0-based)
            character: Character position (0-based)
        
        Returns:
            List of completion items
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🔵 BasicCompletionProvider: line=%s, char=%s", line, character)
        
        # Detect context
        in_parentheses = BasicCompletionProvider._detect_in_parentheses(content, line, character)
        after_colon = BasicCompletionProvider._detect_after_colon(content, line, character)
        
        logger.info("   in_parentheses=%s, after_colon=%s", in_parentheses, after_colon)
        
        # Context 1: Type hints (inside parentheses)
        if in_parentheses:
            logger.info("   → Type hint completions")
            return BasicCompletionProvider._type_hint_completions()
        
        # Context 2: Common values (after colon)
        if after_colon:
            logger.info("   → Common value completions")
            return BasicCompletionProvider._value_completions()
        
        logger.info("   → No completions")
        return []
    
    @staticmethod
    def _detect_in_parentheses(content: str, line: int, character: int) -> bool:
        """Check if cursor is inside type hint parentheses."""
        lines = content.splitlines()
        if line >= len(lines):
            return False
        
        prefix = lines[line][:character]
        
        # Check if we're between ( and )
        open_count = prefix.count('(')
        close_count = prefix.count(')')
        
        return open_count > close_count
    
    @staticmethod
    def _detect_after_colon(content: str, line: int, character: int) -> bool:
        """Check if cursor is after a colon (value position)."""
        lines = content.splitlines()
        if line >= len(lines):
            return False
        
        prefix = lines[line][:character]
        
        # Check if there's a colon followed by whitespace before cursor
        # This prevents triggering on "key:" without space (key definition)
        # Only trigger on "key: " or "key:\t" (value position)
        if ':' not in prefix:
            return False
        
        # Find the last colon
        colon_idx = prefix.rfind(':')
        after_colon = prefix[colon_idx + 1:]
        
        # Trigger only if there's whitespace after colon
        return len(after_colon) > 0 and after_colon[0] in (' ', '\t')
    
    @staticmethod
    def _type_hint_completions() -> List[lsp_types.CompletionItem]:
        """Generate type hint completions from DocumentationRegistry."""
        docs = DocumentationRegistry.get_by_type(DocumentationType.TYPE_HINT)
        
        items = []
        for doc in docs:
            items.append(
                lsp_types.CompletionItem(
                    label=doc.label,
                    kind=lsp_types.CompletionItemKind.TypeParameter,
                    detail=doc.to_completion_detail(),
                    documentation=lsp_types.MarkupContent(
                        kind=lsp_types.MarkupKind.Markdown,
                        value=doc.to_completion_documentation()
                    ),
                    insert_text=doc.label,
                    sort_text=f"0{doc.label}"
                )
            )
        
        return items
    
    @staticmethod
    def _value_completions() -> List[lsp_types.CompletionItem]:
        """Generate common value completions (true, false, null)."""
        docs = DocumentationRegistry.get_by_type(DocumentationType.VALUE)
        
        items = []
        for doc in docs:
            items.append(
                lsp_types.CompletionItem(
                    label=doc.label,
                    kind=lsp_types.CompletionItemKind.Value,
                    detail=doc.to_completion_detail(),
                    documentation=lsp_types.MarkupContent(
                        kind=lsp_types.MarkupKind.Markdown,
                        value=doc.to_completion_documentation()
                    ),
                    insert_text=doc.label,
                    sort_text=f"1{doc.label}"
                )
            )
        
        return items
