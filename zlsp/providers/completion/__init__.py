"""
Completion provider for .zolo files.

Phase 3 Architecture:
- Routes to BasicCompletionProvider or ZVAFCompletionProvider based on file type
- Basic provider: Fast, lightweight completions for generic .zolo files
- zVAF provider: Full-featured completions for zSpark, zUI, zEnv, zConfig, zSchema
"""

from .completion_provider import get_completions
from .completion_router import CompletionRouter
from .registry import CompletionContext, CompletionRegistry

__all__ = [
    'get_completions',
    'CompletionRouter',
    'CompletionContext',
    'CompletionRegistry',
]
