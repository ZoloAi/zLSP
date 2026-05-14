"""
Unit tests for Prism.js pattern generation.

Tests pattern extraction, transformation, and ordering for all file types.
"""

import pytest
import re
from zlsp.parser.zvaf.file_type_detector import FileType
from zlsp.generators.prism_pattern_generator import (
    generate_base_patterns,
    generate_override_patterns_for_file_type,
    generate_language_configs,
    build_prism_base_language,
    build_prism_extended_language,
    generate_test_cases_for_file_type,
)
from zlsp.generators.file_type_pattern_extractor import (
    extract_root_key_patterns,
    extract_nested_key_patterns,
    extract_value_patterns,
    get_file_type_config,
)
from zlsp.generators.prism_pattern_transformer import (
    transform_comment_pattern,
    optimize_pattern_order,
    validate_pattern,
)


class TestPatternExtraction:
    """Test pattern extraction from zlsp SSOT."""
    
    def test_generic_patterns(self):
        """Test base zolo pattern extraction."""
        patterns = generate_base_patterns()
        pattern_names = [p['name'] for p in patterns]

        assert 'comment' in pattern_names
        assert 'root-key' in pattern_names
        assert 'property' in pattern_names
        assert len(patterns) > 5  # At least basic patterns
    
    def test_zspark_patterns(self):
        """Test zSpark-specific override extraction."""
        patterns = generate_override_patterns_for_file_type(FileType.ZSPARK)
        pattern_names = [p['name'] for p in patterns]

        assert 'zspark-root' in pattern_names
        assert 'zspark-nested' in pattern_names
        assert 'zspark-mode-value' in pattern_names
    
    def test_zui_patterns(self):
        """Test zUI-specific override extraction."""
        patterns = generate_override_patterns_for_file_type(FileType.ZUI)
        pattern_names = [p['name'] for p in patterns]

        assert 'zui-special-root' in pattern_names
        assert 'zui-element' in pattern_names
        assert 'zui-element-property' in pattern_names
        assert 'control-flow-key' in pattern_names
        assert 'zrbac-key' in pattern_names
    
    def test_zschema_patterns(self):
        """Test zSchema-specific override extraction."""
        patterns = generate_override_patterns_for_file_type(FileType.ZSCHEMA)
        pattern_names = [p['name'] for p in patterns]

        assert 'zschema-zmeta-root' in pattern_names
        assert 'zschema-zos-data' in pattern_names
        assert 'zschema-property' in pattern_names
    
    def test_zconfig_patterns(self):
        """Test zConfig-specific override extraction."""
        patterns = generate_override_patterns_for_file_type(FileType.ZCONFIG)
        pattern_names = [p['name'] for p in patterns]

        assert 'zconfig-special-root' in pattern_names
        assert 'zmachine-locked-section' in pattern_names
        assert 'zmachine-editable-section' in pattern_names
        assert 'zconfig-property' in pattern_names
    
    def test_zenv_patterns(self):
        """Test zEnv-specific override extraction."""
        patterns = generate_override_patterns_for_file_type(FileType.ZENV)
        pattern_names = [p['name'] for p in patterns]

        assert 'zenv-config-root' in pattern_names
        assert 'zenv-z-uppercase-root' in pattern_names
        assert 'znavbar-nested' in pattern_names
        assert 'zpath-value' in pattern_names
        assert 'env-constant-value' in pattern_names


class TestPatternValidation:
    """Test pattern validation and correctness."""
    
    def test_all_patterns_valid(self):
        """Test that all generated patterns are valid."""
        # Test base patterns
        base_patterns = generate_base_patterns()
        for pattern in base_patterns:
            validate_pattern(pattern)
        
        # Test file-type-specific overrides (skip null overrides)
        for file_type in [FileType.ZSPARK, FileType.ZUI, FileType.ZSCHEMA, 
                          FileType.ZCONFIG, FileType.ZENV]:
            patterns = generate_override_patterns_for_file_type(file_type)
            for pattern in patterns:
                # Skip null patterns (used to disable inherited patterns)
                if pattern.get('pattern') != 'null':
                    validate_pattern(pattern)
    
    def test_root_key_pattern_matches(self):
        """Test root key pattern matches expected inputs.
        
        Note: This is a simplified test since Python regex behaves differently
        from Prism.js's lookbehind implementation. The regression test below
        provides more comprehensive validation.
        """
        patterns = extract_root_key_patterns(FileType.GENERIC)
        root_pattern = next(p for p in patterns if p['name'] == 'root-key')
        
        # Extract regex from /regex/flags format
        pattern_str = root_pattern['pattern']
        regex_match = re.match(r'/(.+)/([a-z]*)', pattern_str)
        assert regex_match, f"Invalid pattern format: {pattern_str}"
        
        # Just validate the pattern has the expected components
        regex_body = regex_match.group(1)
        
        # Check pattern includes capital letter start
        assert '[A-Z]' in regex_body
        # Check pattern matches at line start (capturing or non-capturing group)
        assert ('(^|' in regex_body or '(?:^|' in regex_body or '(?<=\\n)' in regex_body), \
            f"Pattern should match at column 0: {regex_body}"
        # Check pattern has lookahead for colon
        assert '(?=' in regex_body and ':' in regex_body
    
    def test_regression_settings_page_bug(self):
        """Regression test: Settings_Page should be colored as root-key."""
        patterns = extract_root_key_patterns(FileType.GENERIC)
        root_pattern = next(p for p in patterns if p['name'] == 'root-key')
        
        # Extract regex
        pattern_str = root_pattern['pattern']
        regex_match = re.match(r'/(.+)/([a-z]*)', pattern_str)
        regex_body = regex_match.group(1)
        flags_str = regex_match.group(2)
        
        python_flags = re.MULTILINE if 'm' in flags_str else 0
        regex = re.compile(regex_body, python_flags)
        
        # Test that Settings_Page matches after a newline
        test_input = "\nSettings_Page:"
        match = regex.search(test_input)
        assert match is not None, "Settings_Page: should match as root key"


class TestPatternOrdering:
    """Test pattern ordering optimization."""
    
    def test_comments_first(self):
        """Test that comments have highest priority in base."""
        patterns = generate_base_patterns()
        assert patterns[0]['name'] == 'comment', "Comments should be first"
    
    def test_specific_before_generic_roots(self):
        """Test that specific root keys come before generic root-key in overrides."""
        patterns = generate_override_patterns_for_file_type(FileType.ZSPARK)
        pattern_names = [p['name'] for p in patterns]
        
        # Both patterns should exist in overrides to override the base
        assert 'zspark-root' in pattern_names
        assert 'root-key' in pattern_names
        
        zspark_idx = pattern_names.index('zspark-root')
        root_idx = pattern_names.index('root-key')
        assert zspark_idx < root_idx, "Specific zspark-root should override before generic root-key"
    
    def test_punctuation_last(self):
        """Test that punctuation has lowest priority in base."""
        patterns = generate_base_patterns()
        assert patterns[-1]['name'] == 'punctuation', "Punctuation should be last in base"


class TestLanguageDefinitionBuilding:
    """Test JavaScript language definition building."""
    
    def test_builds_valid_javascript(self):
        """Test that generated JavaScript is syntactically valid."""
        patterns = generate_base_patterns()
        js_code = build_prism_base_language(patterns)
        
        # Check basic structure
        assert 'Prism.languages.zolo =' in js_code
        assert js_code.strip().endswith('};')
        
        # Check it has patterns
        assert 'pattern:' in js_code
        assert 'alias:' in js_code
    
    def test_includes_header_comment(self):
        """Test that generated code includes header comment."""
        patterns = generate_override_patterns_for_file_type(FileType.ZSPARK)
        base_patterns = generate_base_patterns()
        js_code = build_prism_extended_language(
            language_name='zspark',
            base_patterns=base_patterns,
            override_patterns=patterns,
            description='zSpark file syntax'
        )
        
        assert '/**' in js_code
        assert 'zspark' in js_code.split('\n')[1]
        assert 'DO NOT EDIT MANUALLY' in js_code
        assert 'Prism.languages.extend' in js_code
    
    def test_all_file_types_build(self):
        """Test that all file types can build valid definitions."""
        # Test base
        base_patterns = generate_base_patterns()
        js_code = build_prism_base_language(base_patterns)
        assert 'Prism.languages.zolo =' in js_code
        assert js_code.strip().endswith('};')
        
        # Test each extended language
        for file_type in [FileType.ZSPARK, FileType.ZUI, FileType.ZSCHEMA, 
                          FileType.ZCONFIG, FileType.ZENV]:
            config = get_file_type_config(file_type)
            patterns = generate_override_patterns_for_file_type(file_type)
            
            js_code = build_prism_extended_language(
                language_name=config['name'],
                base_patterns=base_patterns,
                override_patterns=patterns,
                description=config['description']
            )
            
            # Should have valid structure with extend
            assert f"Prism.languages.{config['name']} = Prism.languages.extend('zolo'," in js_code
            assert 'pattern:' in js_code


class TestLanguageConfigs:
    """Test language configuration generation."""
    
    def test_all_file_types_have_config(self):
        """Test that all file types have language configs."""
        configs = generate_language_configs()
        
        assert FileType.GENERIC in configs
        assert FileType.ZSPARK in configs
        assert FileType.ZUI in configs
        assert FileType.ZSCHEMA in configs
        assert FileType.ZCONFIG in configs
        assert FileType.ZENV in configs
    
    def test_config_has_required_fields(self):
        """Test that configs have all required fields."""
        configs = generate_language_configs()
        
        for file_type, config in configs.items():
            assert 'name' in config
            assert 'displayName' in config
            assert 'description' in config
            
            # Name should be lowercase
            assert config['name'].islower()
            
            # Display name should be human-readable
            assert len(config['displayName']) > 0
            
            # Description should be informative
            assert len(config['description']) > 10


class TestFileTypeSpecificBehavior:
    """Test file-type-specific pattern behavior."""
    
    def test_zspark_only_colors_zspark_root(self):
        """Test that zSpark files only color 'zSpark:' as special root."""
        patterns = extract_root_key_patterns(FileType.ZSPARK)
        
        # Should have zspark-root pattern
        zspark_pattern = next((p for p in patterns if p['name'] == 'zspark-root'), None)
        assert zspark_pattern is not None
        assert 'zSpark' in zspark_pattern['pattern']
        
        # Should also have generic root-key for other capitals
        generic_pattern = next((p for p in patterns if p['name'] == 'root-key'), None)
        assert generic_pattern is not None
    
    def test_zui_has_element_patterns(self):
        """Test that zUI files have UI element patterns."""
        patterns = extract_nested_key_patterns(FileType.ZUI)
        pattern_names = [p['name'] for p in patterns]
        
        assert 'zui-element' in pattern_names
        
        # Check that element pattern includes common elements
        element_pattern = next(p for p in patterns if p['name'] == 'zui-element')
        pattern_str = element_pattern['pattern']
        
        assert 'zH1' in pattern_str or 'zText' in pattern_str or 'zMD' in pattern_str
    
    def test_zschema_has_property_patterns(self):
        """Test that zSchema files have field property patterns."""
        patterns = extract_nested_key_patterns(FileType.ZSCHEMA)
        pattern_names = [p['name'] for p in patterns]
        
        assert 'zschema-property' in pattern_names
        
        # Check that property pattern includes common properties
        prop_pattern = next(p for p in patterns if p['name'] == 'zschema-property')
        pattern_str = prop_pattern['pattern']
        
        assert 'type' in pattern_str or 'pk' in pattern_str
    
    def test_zenv_has_zpath_pattern(self):
        """Test that zEnv files have zPath value pattern."""
        patterns = extract_value_patterns(FileType.ZENV)
        pattern_names = [p['name'] for p in patterns]
        
        assert 'zpath-value' in pattern_names
        
        # Check pattern matches zPath syntax
        zpath_pattern = next(p for p in patterns if p['name'] == 'zpath-value')
        pattern_str = zpath_pattern['pattern']
        
        # Should match @ or ~ prefix
        assert '@' in pattern_str or '~' in pattern_str


class TestGeneratedTestCases:
    """Test that generated test cases are valid."""
    
    def test_all_file_types_have_test_cases(self):
        """Test that all file types have generated test cases."""
        for file_type in FileType:
            test_cases = generate_test_cases_for_file_type(file_type)
            assert len(test_cases) > 0, f"No test cases for {file_type}"
    
    def test_test_cases_have_required_fields(self):
        """Test that test cases have required fields."""
        for file_type in FileType:
            test_cases = generate_test_cases_for_file_type(file_type)
            
            for test_case in test_cases:
                assert 'name' in test_case
                assert 'input' in test_case
                assert 'expected' in test_case
                
                # Expected should be a dict of token mappings
                assert isinstance(test_case['expected'], dict)
