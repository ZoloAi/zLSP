"""
Root Key-Value Parser

Parses root-level key-value pairs (Phase 1).
Simple flat structure with type detection.
"""

from ...basic.value_processors import detect_value_type


def parse_root_key_value_pairs(lines: list[str]) -> dict:
    """
    Phase 1, Steps 1.2-1.3: Parse basic key-value pairs with type detection.
    
    Rules:
    - Only parse lines at root level (no leading whitespace)
    - Split on first `:` occurrence
    - Trim whitespace from key and value
    - Apply RFC 8259 type detection (Step 1.3)
    - Skip nested lines (will be handled in Phase 2)
    
    Args:
        lines: Cleaned lines (from Step 1.1)
    
    Returns:
        Dictionary with root-level key-value pairs (typed values)
    
    Examples:
        >>> parse_root_key_value_pairs(["name: MyApp", "port: 5000"])
        {'name': 'MyApp', 'port': 5000.0}
        
        >>> parse_root_key_value_pairs(["debug: true", "db: null"])
        {'debug': True, 'db': None}
    """
    result = {}

    for line in lines:
        # Check if this is a root-level line (no leading whitespace)
        if line and line[0] not in (' ', '\t'):
            # Check if line contains a colon (key: value pattern)
            if ':' in line:
                # Split on first colon only
                key, _, value = line.partition(':')

                # Trim whitespace
                key = key.strip()
                value = value.strip()

                # Step 1.3: Detect and convert value type
                typed_value = detect_value_type(value)

                result[key] = typed_value

    return result
