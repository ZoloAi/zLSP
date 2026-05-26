"""
zVAF Completion Provider - File-type-specific completions

Provides advanced completions for zVAF file types (zSpark, zUI, zEnv, zConfig, zSchema).
Includes:
- Context-aware key completions from theme YAML
- File-type + key specific value completions
- UI element completions
- Block key detection
- Parent key context analysis
- Indentation-aware completions

All completions are sourced from SSOT:
- Theme YAML: Key and value completions per file type
- key_classifications: UI elements and block keys
- documentation_registry: Type hints and common values
"""

from typing import List, Optional
from lsprotocol import types as lsp_types

from zlsp.parser.zvaf.file_type_detector import FileType, detect_file_type
from ..shared.documentation_registry import DocumentationRegistry, DocumentationType
from ..shared.key_classifications import UI_ELEMENTS


class ZVAFCompletionContext:
    """
    Detected context for zVAF file completions.
    
    Analyzes cursor position, file type, and nesting to provide smart completions.
    """

    def __init__(
        self,
        content: str,
        line: int,
        character: int,
        filename: str
    ):
        self.content = content
        self.line = line
        self.character = character
        self.filename = filename
        self.file_type = detect_file_type(filename)

        # Detect context from cursor position
        self.in_parentheses = self._detect_in_parentheses()
        self.after_colon = self._detect_after_colon()
        self.at_line_start = self._detect_at_line_start()
        self.current_key = self._detect_current_key()

    def _detect_in_parentheses(self) -> bool:
        """Check if cursor is inside type hint parentheses."""
        lines = self.content.splitlines()
        if self.line >= len(lines):
            return False

        prefix = lines[self.line][:self.character]
        open_count = prefix.count('(')
        close_count = prefix.count(')')

        return open_count > close_count

    def _detect_after_colon(self) -> bool:
        """Check if cursor is after a colon (value position)."""
        lines = self.content.splitlines()
        if self.line >= len(lines):
            return False

        prefix = lines[self.line][:self.character]
        
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

    def _detect_at_line_start(self) -> bool:
        """Check if cursor is at the start of a line (key position)."""
        lines = self.content.splitlines()

        if not lines or self.line >= len(lines):
            return True

        line_content = lines[self.line]
        prefix = line_content[:self.character]

        if prefix.strip() == '':
            return True

        if ':' not in line_content:
            return True

        return False

    def _detect_current_key(self) -> Optional[str]:
        """Extract the key name at the current line."""
        lines = self.content.splitlines()
        if self.line >= len(lines):
            return None

        line_content = lines[self.line]

        if ':' in line_content:
            key_part = line_content.split(':')[0].strip()

            if '(' in key_part:
                key_part = key_part.split('(')[0].strip()

            key_part = key_part.lstrip('^~').rstrip('!*')

            return key_part if key_part else None

        return None


class ZVAFCompletionProvider:
    """
    Provides advanced completions for zVAF file types.
    
    Delegates to theme YAML for all key and value completions.
    """

    @staticmethod
    def get_completions(
        content: str,
        line: int,
        character: int,
        filename: str
    ) -> List[lsp_types.CompletionItem]:
        """
        Get completions for zVAF files.
        
        Args:
            content: Full .zolo file content
            line: Line number (0-based)
            character: Character position (0-based)
            filename: Filename for file type detection
        
        Returns:
            List of completion items
        """
        import logging
        logger = logging.getLogger(__name__)

        # Create zVAF context
        context = ZVAFCompletionContext(content, line, character, filename)

        logger.info("🟣 ZVAFCompletionProvider:")
        logger.info("   File: %s", filename)
        logger.info("   File type: %s", context.file_type)
        logger.info("   Line %s, char %s", line, character)
        logger.info("   in_parentheses: %s", context.in_parentheses)
        logger.info("   after_colon: %s", context.after_colon)
        logger.info("   at_line_start: %s", context.at_line_start)
        logger.info("   current_key: %s", context.current_key)

        # Context 1: Type hints (inside parentheses)
        if context.in_parentheses:
            logger.info("   → Type hint completions")
            return ZVAFCompletionProvider._type_hint_completions()

        # Context 2: File-type-specific value completions (after colon)
        if context.after_colon and context.current_key:
            # Skip completions for block-level keys
            if DocumentationRegistry.is_block_key(context.current_key):
                logger.info("   → Skipping value completions for block key '%s'", context.current_key)
                return []

            logger.info("   → File-specific value completions for key '%s'", context.current_key)
            file_completions = ZVAFCompletionProvider._file_specific_completions(
                context.file_type,
                context.current_key
            )
            if file_completions:
                return file_completions

        # Context 3: General value completions (after colon)
        if context.after_colon:
            if context.current_key and DocumentationRegistry.is_block_key(context.current_key):
                logger.info("   → Skipping general value completions for block key '%s'", context.current_key)
                return []

            logger.info("   → General value completions")
            return ZVAFCompletionProvider._value_completions()

        # Context 4: File-type-specific key completions (at line start) - THEME-DRIVEN!
        if context.at_line_start:
            logger.info("   → Theme-driven key completions")
            return ZVAFCompletionProvider._get_key_completions_from_theme(context)

        logger.info("   → No completions")
        return []

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

    @staticmethod
    def _file_specific_completions(
        file_type: FileType,
        key: str
    ) -> Optional[List[lsp_types.CompletionItem]]:
        """
        Generate file-type and key-specific completions from theme YAML (SSOT).
        
        Args:
            file_type: Type of .zolo file (ZSPARK, ZUI, etc.)
            key: Current key name
        
        Returns:
            List of completion items, or None if no specific completions
        """
        # Get value completions from theme
        values = ZVAFCompletionProvider._get_value_completions_from_theme(file_type, key)

        if values:
            # Determine appropriate detail based on key
            detail_map = {
                'zEnv':   'Deployment environment',
                'zState': 'Deployment environment (deprecated)',
                'zLog':   'Logger level',
                'zScrap': 'Logger level (deprecated)',
                'zMode': 'Execution mode',
                'zVaFile': 'zVaFile type',
                'zBlock': 'zBlock type',
                'type': 'Field type',
            }
            detail = detail_map.get(key, f'{key} value')

            return ZVAFCompletionProvider._create_simple_completions(
                values,
                lsp_types.CompletionItemKind.EnumMember,
                detail
            )

        return None

    @staticmethod
    def _get_value_completions_from_theme(
        file_type: FileType,
        key: str
    ) -> List[str]:
        """
        Get value completions for a key from theme YAML (SSOT).
        
        Args:
            file_type: Type of .zolo file
            key: Key name to get values for
        
        Returns:
            List of valid values for this key
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            from ...themes import load_theme, CompletionRegistry as ThemeCompletionRegistry

            theme = load_theme('zolo_default')
            registry = ThemeCompletionRegistry(theme)

            if not registry.is_enabled():
                logger.debug("Theme completions disabled")
                return []

            file_type_key = file_type.value
            values = registry.get_value_completions(file_type_key, key)

            logger.debug(
                "Theme value completions for %s.%s: %s",
                file_type_key, key, values
            )

            return values

        except Exception as e:
            logger.warning("Failed to load theme value completions: %s", e)
            return []

    @staticmethod
    def _create_simple_completions(
        values: List[str],
        kind: lsp_types.CompletionItemKind,
        detail: str
    ) -> List[lsp_types.CompletionItem]:
        """Helper to create simple completion items from a list of values."""
        items = []
        for value in values:
            items.append(
                lsp_types.CompletionItem(
                    label=value,
                    kind=kind,
                    detail=detail,
                    insert_text=value,
                    sort_text=f"0{value}"
                )
            )
        return items

    @staticmethod
    def _get_key_completions_from_theme(context: ZVAFCompletionContext) -> List[lsp_types.CompletionItem]:
        """
        Get file-type-specific key completions from theme config (SSOT approach).
        
        Args:
            context: Completion context with file type and cursor position
        
        Returns:
            List of LSP completion items generated from theme config
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            from ...themes import load_theme, CompletionRegistry as ThemeCompletionRegistry

            theme = load_theme('zolo_default')
            registry = ThemeCompletionRegistry(theme)

            if not registry.is_enabled():
                logger.info("Theme completions disabled")
                return []

            # Detect indentation level and parent key
            indent_level = ZVAFCompletionProvider._get_indent_level(context)
            parent_key = ZVAFCompletionProvider._get_parent_key(context)

            logger.info("   Indent level: %s, Parent key: %s", indent_level, parent_key)

            # Get completions from theme for this context
            file_type_key = context.file_type.value
            theme_completions = registry.get_completions_for_context(
                file_type_key,
                indent_level,
                parent_key
            )

            logger.info("   Theme returned %s completions", len(theme_completions))

            # Convert theme definitions to LSP CompletionItems
            lsp_items = ZVAFCompletionProvider._theme_to_lsp_completions(theme_completions)
            return lsp_items

        except Exception as e:
            logger.error("Failed to load theme completions: %s", e, exc_info=True)
            return []

    @staticmethod
    def _get_indent_level(context: ZVAFCompletionContext) -> int:
        """Get the indentation level at current cursor position."""
        lines = context.content.splitlines()
        if context.line >= len(lines):
            return 0

        current_line = lines[context.line]
        leading_space = current_line[:len(current_line) - len(current_line.lstrip())]
        return len(leading_space)

    @staticmethod
    def _get_parent_key(context: ZVAFCompletionContext) -> Optional[str]:
        """Find the parent key for the current indentation level."""
        lines = context.content.splitlines()
        if context.line <= 0 or context.line >= len(lines):
            return None

        current_indent = ZVAFCompletionProvider._get_indent_level(context)

        # Search backwards for parent
        for i in range(context.line - 1, -1, -1):
            line = lines[i].strip()
            if not line or line.startswith('#'):
                continue

            line_indent = len(lines[i]) - len(lines[i].lstrip())

            # Found parent (less indented line with a key)
            if line_indent < current_indent and ':' in line:
                key = line.split(':')[0].strip()
                return key

        return None

    @staticmethod
    def _theme_to_lsp_completions(theme_completions: List[dict]) -> List[lsp_types.CompletionItem]:
        """Convert theme completion definitions to LSP CompletionItems."""
        items = []

        kind_map = {
            'class': lsp_types.CompletionItemKind.Class,
            'property': lsp_types.CompletionItemKind.Property,
            'value': lsp_types.CompletionItemKind.Value,
            'keyword': lsp_types.CompletionItemKind.Keyword,
            'snippet': lsp_types.CompletionItemKind.Snippet,
        }

        for yaml_item in theme_completions:
            label = yaml_item.get('label', '')
            if not label:
                continue

            kind_str = yaml_item.get('kind', 'property')
            kind = kind_map.get(kind_str, lsp_types.CompletionItemKind.Property)

            detail = yaml_item.get('detail', '')
            documentation = yaml_item.get('documentation', '')
            insert_text = yaml_item.get('insert_text', label + ': ')
            priority = yaml_item.get('priority', 1)
            preselect = yaml_item.get('preselect', False)

            # Check if this is a snippet with placeholder support
            insert_text_format_str = yaml_item.get('insert_text_format', 'plaintext')
            insert_text_format = (
                lsp_types.InsertTextFormat.Snippet
                if insert_text_format_str == 'snippet'
                else lsp_types.InsertTextFormat.PlainText
            )

            items.append(
                lsp_types.CompletionItem(
                    label=label,
                    kind=kind,
                    detail=detail,
                    documentation=lsp_types.MarkupContent(
                        kind=lsp_types.MarkupKind.Markdown,
                        value=documentation
                    ) if documentation else None,
                    insert_text=insert_text,
                    insert_text_format=insert_text_format,
                    sort_text=f"{priority}_{label}",
                    preselect=preselect
                )
            )

        return items

    @staticmethod
    def _ui_element_completions() -> List[lsp_types.CompletionItem]:
        """
        Generate UI element key completions from key_classifications SSOT.
        """
        items = []

        for element in UI_ELEMENTS:
            items.append(
                lsp_types.CompletionItem(
                    label=element.label,
                    kind=lsp_types.CompletionItemKind.Class,
                    detail=element.detail,
                    documentation=lsp_types.MarkupContent(
                        kind=lsp_types.MarkupKind.Markdown,
                        value=element.documentation
                    ),
                    insert_text=element.insert_text,
                    sort_text=f"{element.priority}{element.label}"
                )
            )

        return items
