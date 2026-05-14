"""
zVaF-Specific Parser Components - Domain-specific knowledge

These modules contain zVaF-specific logic including file type detection,
special key recognition, zVaF value validation rules, and modifier handling.
"""

from ..basic.block_tracker import BlockTracker
from .file_type_detector import (
    FileType,
    FileTypeDetector,
    detect_file_type,
    extract_component_name,
    get_file_info,
)
from .value_validators import ValueValidator, validate_special_value
from .value_validator_callback import validate_for_key_callback
from .key_detector import KeyDetector, detect_key_type
from .modifier_handler import ModifierHandler, emit_key_with_modifiers
from .ui_shortcuts import is_ui_event_shorthand, handle_duplicate_ui_key
from .multiline_detection import check_auto_multiline_for_key
from .zvaf_parser import parse_lines_zvaf

__all__ = [
    'BlockTracker',
    'FileType',
    'FileTypeDetector',
    'detect_file_type',
    'extract_component_name',
    'get_file_info',
    'ValueValidator',
    'validate_special_value',
    'validate_for_key_callback',
    'KeyDetector',
    'detect_key_type',
    'ModifierHandler',
    'emit_key_with_modifiers',
    'is_ui_event_shorthand',
    'handle_duplicate_ui_key',
    'check_auto_multiline_for_key',
    'parse_lines_zvaf',
]
