"""
Tests for escaped comma support in split_on_comma function.

The \, escape allows commas to appear in array/object values without
being treated as delimiters. This is particularly useful for:
- Function signatures: method(key, default)
- Table rows with complex column values
- Any comma-separated data that contains literal commas
"""

import unittest
from zlsp.parser.basic.value_processors import (
    split_on_comma,
    parse_bracket_array,
    parse_brace_object
)


class TestEscapedComma(unittest.TestCase):
    """Test escaped comma (\,) functionality."""
    
    def test_basic_split_no_escapes(self):
        """Test that basic splitting still works without escapes."""
        result = split_on_comma('a, b, c')
        self.assertEqual(result, ['a', ' b', ' c'])
    
    def test_nested_brackets_no_escapes(self):
        """Test that nested bracket protection still works."""
        result = split_on_comma('a: [1, 2], b: 3')
        self.assertEqual(result, ['a: [1, 2]', ' b: 3'])
    
    def test_single_escaped_comma(self):
        """Test a single escaped comma in the middle of a value."""
        result = split_on_comma(r'func(x\, y), other')
        self.assertEqual(result, ['func(x, y)', ' other'])
    
    def test_multiple_escaped_commas(self):
        """Test multiple escaped commas in different parts."""
        result = split_on_comma(r'method(key\, default), description\, note, returns')
        self.assertEqual(result, ['method(key, default)', ' description, note', ' returns'])
    
    def test_escaped_comma_at_start(self):
        """Test escaped comma at the beginning of a value."""
        result = split_on_comma(r'\,start, middle, end')
        self.assertEqual(result, [',start', ' middle', ' end'])
    
    def test_escaped_comma_at_end(self):
        """Test escaped comma at the end of a value."""
        result = split_on_comma(r'start, middle, end\,')
        self.assertEqual(result, ['start', ' middle', ' end,'])
    
    def test_consecutive_escaped_commas(self):
        """Test multiple consecutive escaped commas."""
        result = split_on_comma(r'value\,\,\,, next')
        self.assertEqual(result, ['value,,,', ' next'])
    
    def test_escaped_comma_in_bracket_array(self):
        """Test escaped comma works in parse_bracket_array."""
        result = parse_bracket_array(r'[func(a\, b), other]')
        self.assertEqual(result, ['func(a, b)', 'other'])
    
    def test_escaped_comma_in_brace_object(self):
        """Test escaped comma works in parse_brace_object."""
        result = parse_brace_object(r'{method: get(x\, y), desc: test}')
        self.assertEqual(result, {'method': 'get(x, y)', 'desc': 'test'})
    
    def test_table_row_with_function_signature(self):
        """Test realistic table row with function signature containing comma."""
        row = r'[z.config.environment.get_env_var(key\, default), Get environment variable with fallback, str]'
        result = parse_bracket_array(row)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 'z.config.environment.get_env_var(key, default)')
        self.assertEqual(result[1], 'Get environment variable with fallback')
        self.assertEqual(result[2], 'str')
    
    def test_mixed_escaped_and_nested(self):
        """Test escaped commas combined with nested brackets."""
        result = split_on_comma(r'func(a\, b), [1, 2], other\, value')
        self.assertEqual(result, ['func(a, b)', ' [1, 2]', ' other, value'])
    
    def test_escape_preserved_in_nested_structure(self):
        """Test that escapes are preserved inside nested brackets (processed at inner level)."""
        # When parsing nested arrays, escapes should be preserved until inner parsing
        result = split_on_comma(r'[x\, y], z')
        # The escape is preserved inside the brackets
        self.assertEqual(result, [r'[x\, y]', ' z'])
        
        # But when we parse the inner array, the escape is processed
        from zlsp.parser.basic.value_processors import parse_bracket_array
        inner_result = parse_bracket_array(result[0])
        self.assertEqual(inner_result, ['x, y'])  # Comma preserved in final value
    
    def test_backslash_not_before_comma(self):
        """Test that backslashes not followed by comma are preserved."""
        result = split_on_comma(r'path\to\file, other')
        self.assertEqual(result, [r'path\to\file', ' other'])
    
    def test_empty_parts_with_escaped_commas(self):
        """Test that empty parts work with escaped commas."""
        result = split_on_comma(r'a\,, , c')
        self.assertEqual(result, ['a,', ' ', ' c'])


if __name__ == '__main__':
    unittest.main()
