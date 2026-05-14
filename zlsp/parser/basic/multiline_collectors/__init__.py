"""
Multiline Collectors - Collect multi-line values

Pure string processing, no dependencies.
Handles: (str) hints, dash lists, bracket arrays, pipes, triple quotes.

SEMANTIC MULTILINE JOINING:
- zText properties → Join with ' ' (space) for .zolo readability
- zMD properties → Context-aware:
    * Inside code blocks (```): '\n' (preserve formatting)
    * Lines ending with '  ': '\n' for <br>
    * Normal lines: ' ' (space)
- Other properties → Join with '\n' (default/backward compatible)
"""

# Special character to mark zMD natural multilines (Unit Separator)
# This allows renderers to distinguish from explicit \n escapes
YAML_LINE_BREAK = '\x1F'

from .str_hint import collect_str_hint_multiline
from .dash_list import collect_dash_list
from .bracket_array import collect_bracket_array
from .pipe import collect_pipe_multiline
from .triple_quote import collect_triple_quote_multiline

__all__ = [
    'YAML_LINE_BREAK',
    'collect_str_hint_multiline',
    'collect_dash_list',
    'collect_bracket_array',
    'collect_pipe_multiline',
    'collect_triple_quote_multiline',
]
