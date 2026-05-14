"""
Basic Provider - Completions for generic .zolo files

Handles core .zolo features that are file-type agnostic:
- Type hints (int, float, bool, str, list, dict, null, raw, date, time, url, path)
- Common values (true, false, null)
- Basic key-value completions

Used for generic .zolo files that don't require zVAF extensions.
"""

from .basic_completion_provider import BasicCompletionProvider

__all__ = [
    'BasicCompletionProvider',
]
