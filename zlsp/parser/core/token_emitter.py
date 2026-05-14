"""
Token Emitter - Semantic token emission with unified block tracking

Now using BlockTracker - replacing 17+ individual tracking lists! 🎉
"""

from typing import List, Optional, Tuple

from zlsp.lsp_types import SemanticToken, Position, Range, Diagnostic
from zlsp.token_types import TokenType
from ..basic.block_tracker import BlockTracker


def _char_to_utf16_offset(text: str, char_offset: int) -> int:
    """
    Convert Python character offset to UTF-16 code unit offset.
    
    LSP uses UTF-16 positions, but Python uses Unicode code points.
    This matters for emoji and characters outside the Basic Multilingual Plane.
    
    Args:
        text: Line text
        char_offset: Character offset in Python string
    
    Returns:
        UTF-16 code unit offset for LSP
    """
    # Take substring up to the character offset
    substring = text[:char_offset]
    # Encode to UTF-16LE and count bytes, divide by 2 for code units
    utf16_bytes = substring.encode('utf-16-le')
    return len(utf16_bytes) // 2


class TokenEmitter:
    """
    Semantic token emitter with unified block tracking.
    
    Tracks parsing context (file type, nested blocks) and emits semantic tokens
    for LSP clients to enable syntax highlighting.
    
    Uses BlockTracker for DRY block context management.
    """

    def __init__(
        self,
        content: str,
        filename: Optional[str] = None,
        is_zui_file: bool = False,
        is_zenv_file: bool = False,
        is_zspark_file: bool = False,
        is_zconfig_file: bool = False,
        is_zschema_file: bool = False,
        zui_component_name: Optional[str] = None,
        zspark_component_name: Optional[str] = None,
        zconfig_component_name: Optional[str] = None
    ):
        """
        Initialize token emitter.
        
        Args:
            content: File content to parse
            filename: Optional filename (for reference only)
            is_zui_file: Whether this is a zUI file
            is_zenv_file: Whether this is a zEnv file
            is_zspark_file: Whether this is a zSpark file
            is_zconfig_file: Whether this is a zConfig file
            is_zschema_file: Whether this is a zSchema file
            zui_component_name: Component name for zUI files (e.g., "zVaF")
            zspark_component_name: Component name for zSpark files
            zconfig_component_name: Component name for zConfig files
        """
        self.content = content
        self.lines = content.splitlines(keepends=False)  # Keep lines for UTF-16 conversion
        self.tokens: List[SemanticToken] = []
        self.diagnostics: List[Diagnostic] = []  # Validation errors and warnings
        self.comment_ranges: List[Tuple[int, int, int, int]] = []  # [(start_line, start_col, end_line, end_col), ...]
        self.filename = filename

        # File type info (passed from caller instead of detecting internally)
        self.is_zui_file = is_zui_file
        self.is_zenv_file = is_zenv_file
        self.is_zspark_file = is_zspark_file
        self.is_zconfig_file = is_zconfig_file
        self.is_zschema_file = is_zschema_file

        # Component names (for zUI.zVaF.zolo -> "zVaF", etc.)
        self.zui_component_name = zui_component_name
        self.zspark_component_name = zspark_component_name
        self.zconfig_component_name = zconfig_component_name

        # 🎉 UNIFIED BLOCK TRACKING - replaces 17+ individual lists!
        self.block_tracker = BlockTracker()

    # ========================================================================
    # COMMENT TRACKING
    # ========================================================================

    def add_comment_range(self, start_line: int, start_col: int, end_line: int, end_col: int):
        """Track a comment range to avoid overlapping tokens."""
        self.comment_ranges.append((start_line, start_col, end_line, end_col))

    # ========================================================================
    # BLOCK TRACKING - Now using BlockTracker! 🚀
    # ========================================================================

    def enter_block(self, block_type: str, indent: int, line: int, data: Optional[str] = None):
        """Enter a new block context (delegates to BlockTracker)."""
        self.block_tracker.enter_block(block_type, indent, line, data)

    def enter_block_single(self, block_type: str, indent: int, line: int):
        """Enter a single-instance block (ZNAVBAR, zMeta) - delegates to BlockTracker."""
        self.block_tracker.enter_block_single(block_type, indent, line)

    def update_blocks(self, current_indent: int, current_line: int):
        """Update all block contexts based on indentation - delegates to BlockTracker."""
        self.block_tracker.update_blocks(current_indent, current_line)

    def is_inside_block(self, block_type: str, current_indent: int) -> bool:
        """Check if inside a block - delegates to BlockTracker."""
        return self.block_tracker.is_inside(block_type, current_indent)

    def is_first_level_in_block(self, block_type: str, current_indent: int) -> bool:
        """Check if at first nesting level under a block - delegates to BlockTracker."""
        return self.block_tracker.is_first_level(block_type, current_indent)

    def is_at_depth_in_block(self, block_type: str, current_indent: int, min_depth: int = 1) -> bool:
        """Check if at specific depth in a block - delegates to BlockTracker."""
        return self.block_tracker.is_at_depth(block_type, current_indent, min_depth)

    def get_block_data(self, block_type: str) -> Optional[str]:
        """Get additional data from a block - delegates to BlockTracker."""
        return self.block_tracker.get_block_data(block_type)

    # ========================================================================
    # TOKEN EMISSION
    # ========================================================================

    def emit_zpath_tokens(self, value: str, line: int, start_pos: int):
        """
        Emit semantic token for zPath syntax.
        
        zPath format: @.static.brand.logo.png or ~.config.theme
        The entire zPath is colored with a single semantic token (cyan: ZPATH_VALUE)
        
        Args:
            value: The zPath string (e.g., "@.static.brand.logo.png")
            line: Line number
            start_pos: Starting character position
        """
        if not value:
            return

        # Emit the entire zPath value as a single token
        self.emit(line, start_pos, len(value), TokenType.ZPATH_VALUE)

    def _overlaps_comment(self, line: int, start: int, end: int) -> bool:
        """Check if a position range overlaps with any comment."""
        for c_start_line, c_start_col, c_end_line, c_end_col in self.comment_ranges:
            if line == c_start_line == c_end_line:
                # Same line comment
                if not (end <= c_start_col or start >= c_end_col):
                    return True
            elif line == c_start_line:
                # Token on comment start line
                if start < c_start_col:
                    continue  # Token is before comment
                return True  # Token starts in or after comment start
            elif c_start_line < line < c_end_line:
                # Token is on a middle line of multi-line comment
                return True
            elif line == c_end_line:
                # Token on comment end line
                if end > c_end_col:
                    continue  # Token is after comment
                return True  # Token ends in or before comment end
        return False

    def emit(self, line: int, start_char: int, length: int, token_type: TokenType):
        """
        Emit a semantic token with UTF-16 position conversion.
        
        This is the LOW-LEVEL token emission function called by all other emitters.
        Handles two critical concerns:
        1. Comment overlap prevention (don't highlight code inside comments)
        2. UTF-16 conversion (LSP requires UTF-16, Python uses Unicode code points)
        
        Args:
            line: Line number (0-based)
            start_char: Character offset in Python string (NOT UTF-16)
            length: Length in Python characters (NOT UTF-16)
            token_type: Token type
        """
        if length <= 0:
            return

        # Get the line text for UTF-16 conversion
        if line >= len(self.lines):
            return
        line_text = self.lines[line]

        # ===== COMMENT OVERLAP PREVENTION =====
        # Don't emit tokens for code that's been commented out!
        # Example: "key: value # comment" - don't highlight "comment" as a key
        if token_type != TokenType.COMMENT:
            end_char = start_char + length

            # Check if this token overlaps any comment
            for c_start_line, c_start_col, _c_end_line, _c_end_col in self.comment_ranges:
                if line == c_start_line and start_char < c_start_col < end_char:
                    # Token would extend into a comment - truncate it
                    # Example: "ke# comment" - truncate to just "ke"
                    length = c_start_col - start_char
                    end_char = start_char + length
                    if length <= 0:
                        return  # Token is entirely within comment
                    break

        # ===== UTF-16 CONVERSION =====
        # LSP protocol requires UTF-16 positions (historical reasons: JavaScript/TypeScript)
        # Python uses Unicode code points (correct way)
        # This matters for emoji (💀 = 2 UTF-16 units, 1 code point) and rare characters
        utf16_start = _char_to_utf16_offset(line_text, start_char)
        utf16_end = _char_to_utf16_offset(line_text, start_char + length)

        # Create and append token
        token = SemanticToken(
            range=Range(
                start=Position(line=line, character=utf16_start),
                end=Position(line=line, character=utf16_end)
            ),
            token_type=token_type
        )
        self.tokens.append(token)

    def emit_range(self, start_line: int, start_char: int, end_line: int, end_char: int, token_type: TokenType):
        """
        Emit a token with explicit start and end positions (UTF-16 converted).
        
        Args:
            start_line: Start line number
            start_char: Start character offset in Python string
            end_line: End line number
            end_char: End character offset in Python string
            token_type: Token type
        """
        # Convert positions to UTF-16
        if start_line >= len(self.lines) or end_line >= len(self.lines):
            return

        start_line_text = self.lines[start_line]
        end_line_text = self.lines[end_line]

        utf16_start = _char_to_utf16_offset(start_line_text, start_char)
        utf16_end = _char_to_utf16_offset(end_line_text, end_char)

        token = SemanticToken(
            range=Range(
                start=Position(line=start_line, character=utf16_start),
                end=Position(line=end_line, character=utf16_end)
            ),
            token_type=token_type
        )
        self.tokens.append(token)

    def get_tokens(self) -> List[SemanticToken]:
        """Get all emitted tokens, sorted by position."""
        return sorted(self.tokens, key=lambda t: (t.line, t.start_char))
