"""
Value Validator Callback - zVaF extension for core value emission

Provides callback function for value_emitters to validate zVaF-specific values.
This decouples core from zvaf while allowing zvaf to inject its validation logic.
"""

from .value_validators import ValueValidator


def validate_for_key_callback(key: str, value: str, line: int, start_pos: int, emitter) -> None:
    """
    Callback for core value_emitters to validate zVaF-specific values.
    
    This function signature matches what core/value_emitters expects.
    
    Args:
        key: The key name
        value: The value to validate
        line: Line number
        start_pos: Start position in line
        emitter: Token emitter (for adding diagnostics)
    """
    ValueValidator.validate_for_key(key, value, line, start_pos, emitter)
