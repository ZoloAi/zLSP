"""
Value Validators - Context-aware value validation

Validates special values in different .zolo file types and generates diagnostics.
Separates validation logic from token emission for cleaner architecture.
"""

from typing import Optional, TYPE_CHECKING

from zlsp.lsp_types import Diagnostic, Range, Position
from ..basic.error_formatter import ErrorFormatter, did_you_mean

if TYPE_CHECKING:
    from .token_emitter import TokenEmitter


class ValueValidator:
    """
    Context-aware value validator for special .zolo file types.
    
    Validates values based on file type and key context, generating
    appropriate diagnostics for invalid values.
    """
    
    # Valid values for each special key
    # zEnv: engine deployment modes (config_environment.py) — accepted in both
    # Title case and the lowercase spelling used throughout zAgents/src examples
    # (`zEnv: development` loads zEnv.development.zolo).
    # zLog: app levels + z-prefixed engine-trace variants (zINFO…) per 01_zspark.md.
    _ZENV_MODES = {'Production', 'Development', 'Testing', 'Debug'}
    _ZLOG_LEVELS = {
        'DEBUG', 'SESSION', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'PROD',
        'zDEBUG', 'zSESSION', 'zINFO', 'zWARNING', 'zERROR', 'zCRITICAL',
    }
    VALID_VALUES = {
        'zMode':  {'zCLI', 'zBifrost'},
        'zEnv':   _ZENV_MODES | {v.lower() for v in _ZENV_MODES},
        'zState': _ZENV_MODES | {v.lower() for v in _ZENV_MODES},   # deprecated → zEnv
        'zLog':   _ZLOG_LEVELS,
        'zScrap': _ZLOG_LEVELS,  # deprecated → zLog
    }
    
    @staticmethod
    def validate_zmode(value: str, line: int, start_pos: int) -> Optional[Diagnostic]:
        """
        Validate zMode value (zCLI/zBifrost).
        
        Args:
            value: The value to validate
            line: Line number
            start_pos: Start position
            
        Returns:
            Diagnostic if invalid, None if valid
        """
        valid_values = ValueValidator.VALID_VALUES['zMode']
        if value not in valid_values:
            msg = ErrorFormatter.format_invalid_value_error(
                key='zMode',
                value=value,
                valid_values=sorted(valid_values),
                line=line
            )
            return Diagnostic(
                range=Range(
                    start=Position(line=line, character=start_pos),
                    end=Position(line=line, character=start_pos + len(value))
                ),
                message=msg,
                severity=1,  # Error
                source="zolo-lsp"
            )
        return None
    
    @staticmethod
    def validate_deployment(value: str, line: int, start_pos: int) -> Optional[Diagnostic]:
        """
        Validate zEnv value (Production/Development/Testing/Debug, either case).
        
        Args:
            value: The value to validate
            line: Line number
            start_pos: Start position
            
        Returns:
            Diagnostic if invalid, None if valid
        """
        valid_values = ValueValidator.VALID_VALUES['zEnv']
        if value not in valid_values:
            msg = ErrorFormatter.format_invalid_value_error(
                key='zEnv',
                value=value,
                valid_values=sorted(valid_values),
                line=line
            )
            return Diagnostic(
                range=Range(
                    start=Position(line=line, character=start_pos),
                    end=Position(line=line, character=start_pos + len(value))
                ),
                message=msg,
                severity=1,  # Error
                source="zolo-lsp"
            )
        return None
    
    @staticmethod
    def validate_logger(value: str, line: int, start_pos: int) -> Optional[Diagnostic]:
        """
        Validate logger value (valid log levels).
        
        Args:
            value: The value to validate
            line: Line number
            start_pos: Start position
            
        Returns:
            Diagnostic if invalid, None if valid
        """
        valid_values = ValueValidator.VALID_VALUES['zLog']
        if value not in valid_values:
            msg = ErrorFormatter.format_invalid_value_error(
                key='zLog',
                value=value,
                valid_values=sorted(valid_values),
                line=line
            )
            return Diagnostic(
                range=Range(
                    start=Position(line=line, character=start_pos),
                    end=Position(line=line, character=start_pos + len(value))
                ),
                message=msg,
                severity=1,  # Error
                source="zolo-lsp"
            )
        return None
    
    @staticmethod
    def validate_zvafile(value: str, line: int, start_pos: int) -> Optional[Diagnostic]:
        """
        Validate zVaFile value (must be zUI.*).
        
        Args:
            value: The value to validate
            line: Line number
            start_pos: Start position
            
        Returns:
            Diagnostic if invalid, None if valid
        """
        if not value.startswith('zUI.'):
            return Diagnostic(
                range=Range(
                    start=Position(line=line, character=start_pos),
                    end=Position(line=line, character=start_pos + len(value))
                ),
                message=f"Invalid zVaFile value: '{value}'. Must start with 'zUI.' (e.g., 'zUI.zBreakpoints').",
                severity=1,  # Error
                source="zolo-lsp"
            )
        return None
    
    @staticmethod
    def validate_zblock(value: str, line: int, start_pos: int) -> Optional[Diagnostic]:
        """
        Validate zBlock value (free-form string for naming).
        
        Args:
            value: The value to validate
            line: Line number
            start_pos: Start position
            
        Returns:
            Diagnostic if invalid, None if valid (always None - zBlock values are plain strings)
        """
        # zBlock values are just plain strings for naming purposes
        # No validation needed - any string is valid
        return None
    
    @staticmethod
    def validate_for_key(
        key: str,
        value: str,
        line: int,
        start_pos: int,
        emitter: 'TokenEmitter'
    ) -> bool:
        """
        Validate value based on key context and add diagnostic if invalid.
        
        Args:
            key: The key name
            value: The value to validate
            line: Line number
            start_pos: Start position
            emitter: TokenEmitter to add diagnostics to
            
        Returns:
            True if validation was performed (regardless of result), False if no validation for this key
        """
        diagnostic = None
        
        # zSpark-specific validations
        if emitter.is_zspark_file:
            if key == 'zMode':
                diagnostic = ValueValidator.validate_zmode(value, line, start_pos)
            elif key in ('zEnv', 'zState'):
                diagnostic = ValueValidator.validate_deployment(value, line, start_pos)
            elif key in ('zLog', 'zScrap'):
                diagnostic = ValueValidator.validate_logger(value, line, start_pos)
            elif key == 'zVaFile':
                diagnostic = ValueValidator.validate_zvafile(value, line, start_pos)
            elif key == 'zBlock':
                diagnostic = ValueValidator.validate_zblock(value, line, start_pos)
            else:
                return False  # No validation for this key
            
            if diagnostic:
                emitter.diagnostics.append(diagnostic)
            return True
        
        return False  # No validation performed


# Helper function for backward compatibility
def validate_special_value(
    key: str,
    value: str,
    line: int,
    start_pos: int,
    emitter: 'TokenEmitter'
) -> bool:
    """
    Convenience function to validate special values.
    
    Args:
        key: The key name
        value: The value to validate
        line: Line number
        start_pos: Start position
        emitter: TokenEmitter to add diagnostics to
        
    Returns:
        True if validation was performed, False otherwise
    """
    return ValueValidator.validate_for_key(key, value, line, start_pos, emitter)
