"""
zVAF Provider - Completions for zVAF-specific .zolo files

Handles advanced zVAF features for special file types:
- zSpark.*.zolo - Spark configuration
- zUI.*.zolo - UI components
- zEnv.*.zolo - Environment configuration
- zConfig.*.zolo - System configuration
- zSchema.*.zolo - Data schema definitions

Includes:
- File-type-specific key completions
- Value completions (zState, zScrap, zMode, etc.)
- UI element completions (zImage, zText, zH1-zH6, etc.)
- Modifier support (^, ~, !, *)
"""

from .zvaf_completion_provider import ZVAFCompletionProvider

__all__ = [
    'ZVAFCompletionProvider',
]
