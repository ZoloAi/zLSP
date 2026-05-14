"""
LSP Type Definitions for .zolo Language Server

Defines position tracking and semantic token types for the Language Server Protocol.
"""

from dataclasses import dataclass, field
from typing import List

# Import TokenType from centralized module
from .token_types import TokenType


@dataclass
class Position:
    """Position in a text document (0-based line and character)."""
    line: int  # 0-based
    character: int  # 0-based

    def __lt__(self, other):
        """Compare positions for ordering."""
        if self.line != other.line:
            return self.line < other.line
        return self.character < other.character

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other


@dataclass
class Range:
    """Range in a text document (start and end positions)."""
    start: Position
    end: Position

    def contains(self, position: Position) -> bool:
        """Check if a position is within this range."""
        return self.start <= position <= self.end

    def overlaps(self, other: 'Range') -> bool:
        """Check if this range overlaps with another range."""
        return (self.start <= other.end and other.start <= self.end)


@dataclass
class SemanticToken:
    """Semantic token with position, type, and optional modifiers."""
    range: Range
    token_type: TokenType
    modifiers: List[str] = field(default_factory=list)

    @property
    def line(self) -> int:
        """Convenience property for token line number."""
        return self.range.start.line

    @property
    def start_char(self) -> int:
        """Convenience property for token start character."""
        return self.range.start.character

    @property
    def length(self) -> int:
        """
        Calculate token length.
        For multi-line tokens, this is the character span on the last line
        (LSP semantic tokens are line-relative).
        """
        if self.range.start.line == self.range.end.line:
            return self.range.end.character - self.range.start.character
        # Multi-line token: for LSP encoding, we use end position as length
        # This allows the encoder to properly represent the multi-line span
        return self.range.end.character

    def __repr__(self):
        # Handle both TokenType enum and int values
        token_value = self.token_type.value if hasattr(self.token_type, 'value') else self.token_type
        return (
            f"SemanticToken(line={self.line}, "
            f"start={self.start_char}, "
            f"length={self.length}, "
            f"type={token_value})"
        )

@dataclass
class Diagnostic:
    """Diagnostic message (error, warning, etc.) for LSP."""
    range: Range
    message: str
    severity: int = 1  # 1=Error, 2=Warning, 3=Info, 4=Hint
    source: str = "zolo-lsp"

@dataclass
class ParseResult:
    """Result of parsing a .zolo file with both data and tokens."""
    data: any  # Parsed data structure
    tokens: List[SemanticToken]  # Semantic tokens for LSP
    errors: List[str] = field(default_factory=list)  # Parse errors (deprecated, use diagnostics)
    diagnostics: List[Diagnostic] = field(default_factory=list)  # Structured diagnostics
