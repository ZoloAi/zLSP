"""
Integration tests for Prism.js pattern generation.

Tests the complete generation pipeline for all 6 languages.

The generator writes a single committed bundle to zlsp/generated/ — package
data served by zOS.zServer at /zsyntax/<version>/ via zlsp.bifrost_prism_dir()
(no manual handoff, no cross-repo deployment).
"""

import subprocess
import pytest
from pathlib import Path


ALL_LANGUAGES = ['zolo', 'zspark', 'zui', 'zschema', 'zconfig', 'zenv']

# Case-preserving code-fence aliases emitted at the end of extended files
CASE_ALIASES = {
    'zspark': 'zSpark',
    'zui': 'zUI',
    'zschema': 'zSchema',
    'zconfig': 'zConfig',
    'zenv': 'zEnv',
}


@pytest.fixture
def project_root():
    """Get zLSP repo root directory."""
    return Path(__file__).parent.parent.parent


# Captured at IMPORT time — before any test below runs the generator and
# refreshes the bundle in place — so the staleness check sees what was
# actually committed, not what a sibling test just regenerated.
_BUNDLE_DIR = Path(__file__).parent.parent.parent / 'zlsp' / 'generated'
_COMMITTED_BUNDLE = {
    f.name: f.read_text()
    for f in sorted(_BUNDLE_DIR.glob('prism-*.js'))
} if _BUNDLE_DIR.is_dir() else {}


class TestBundleFreshness:
    """The committed bundle must match the current grammar SSOT.

    zOS serves zlsp/generated/ straight from the installed wheel — a stale
    committed bundle means every deployed app highlights with an old grammar.
    This is the drift class the /zsyntax/ seam exists to kill; keep it dead.
    """

    def test_committed_bundle_matches_generator_output(self, project_root):
        result = subprocess.run(
            ['python3', '-m', 'zlsp.generators.generate_prism_zolo'],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Generator failed:\n{result.stderr}"

        stale = []
        for language in ALL_LANGUAGES:
            name = f'prism-{language}.js'
            fresh = (_BUNDLE_DIR / name).read_text()
            if _COMMITTED_BUNDLE.get(name) != fresh:
                stale.append(name)
        assert not stale, (
            f"Committed bundle is STALE vs the grammar SSOT: {stale}. "
            "Run `python3 -m zlsp.generators.generate_prism_zolo` (and the CSS "
            "generator) and commit zlsp/generated/ with your grammar change."
        )


@pytest.fixture
def bundle_dir(project_root):
    """Get the single committed output bundle (zlsp/generated/, package data)."""
    return project_root / 'zlsp' / 'generated'


class TestGenerationPipeline:
    """Test the complete generation pipeline."""

    def test_generator_runs_successfully(self, project_root):
        """Test that generator script runs without errors."""
        result = subprocess.run(
            ['python3', '-m', 'zlsp.generators.generate_prism_zolo'],
            cwd=project_root,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Generator failed:\n{result.stderr}"
        assert 'Generation complete!' in result.stdout
        assert 'generated' in result.stdout, \
            "Generator should report the zlsp/generated bundle as its output"

    def test_all_languages_generated(self, bundle_dir):
        """Test that all 6 language files exist in the bundle."""
        for language in ALL_LANGUAGES:
            path = bundle_dir / f'prism-{language}.js'
            assert path.exists(), f"prism-{language}.js not generated in {bundle_dir}"
            assert path.stat().st_size > 0, f"prism-{language}.js is empty"

    def test_generator_output_is_deterministic(self, project_root, bundle_dir):
        """Test that re-running the generator produces identical bundle content."""
        def run_generator():
            result = subprocess.run(
                ['python3', '-m', 'zlsp.generators.generate_prism_zolo'],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Generator failed:\n{result.stderr}"

        run_generator()
        first = {
            language: (bundle_dir / f'prism-{language}.js').read_text()
            for language in ALL_LANGUAGES
        }

        run_generator()
        for language in ALL_LANGUAGES:
            second = (bundle_dir / f'prism-{language}.js').read_text()
            assert first[language] == second, \
                f"prism-{language}.js changed between generator runs"


class TestGeneratedFileContent:
    """Test the content of generated files."""

    @pytest.fixture(params=ALL_LANGUAGES)
    def language_name(self, request):
        return request.param

    @pytest.fixture
    def language_file(self, bundle_dir, language_name):
        return bundle_dir / f'prism-{language_name}.js'

    def test_file_has_prism_definition(self, language_file, language_name):
        """Test that file defines Prism.languages correctly."""
        content = language_file.read_text()
        assert f'Prism.languages.{language_name}' in content

    def test_file_has_header_comment(self, language_file):
        """Test that file has generation header."""
        content = language_file.read_text()
        assert '/**' in content
        assert 'Generated by zlsp/zlsp/generators/generate_prism_zolo.py' in content
        assert 'DO NOT EDIT MANUALLY' in content

    def test_file_has_comment_pattern(self, language_file):
        """Test that all files have comment pattern (in base or inherited)."""
        content = language_file.read_text()

        is_base = 'Prism.languages.zolo = {' in content
        is_extended = "Prism.languages.extend('zolo'," in content

        if is_base:
            # Base zolo should have comment pattern explicitly
            assert "'comment':" in content or '"comment":' in content
            assert '#' in content  # Comment pattern includes #
        elif is_extended:
            # Extended languages inherit comment from base zolo
            assert "Prism.languages.extend('zolo'," in content
        else:
            pytest.fail("File doesn't match base or extended pattern structure")

    def test_file_has_punctuation_pattern(self, language_file):
        """Test punctuation handling: base defines 'colon' aliased to punctuation."""
        content = language_file.read_text()

        is_base = 'Prism.languages.zolo = {' in content
        is_extended = "Prism.languages.extend('zolo'," in content

        if is_base:
            # Base zolo defines the colon separator, aliased to 'punctuation'
            assert "'colon':" in content or '"colon":' in content
            assert "alias: 'punctuation'" in content or 'alias: "punctuation"' in content
        elif is_extended:
            # Extended languages inherit it from base zolo
            assert "Prism.languages.extend('zolo'," in content
        else:
            pytest.fail("File doesn't match base or extended pattern structure")

    def test_file_ends_properly(self, language_file, language_name):
        """Test file ending: base ends with '};', extended with a case alias line."""
        content = language_file.read_text().strip()

        if language_name == 'zolo':
            assert content.endswith('};'), "Base language should end with '};'"
        else:
            # Extended files end with the case-preserving code-fence alias,
            # e.g. Prism.languages.zSpark = Prism.languages.zspark;
            case_alias = CASE_ALIASES[language_name]
            expected_ending = (
                f'Prism.languages.{case_alias} = Prism.languages.{language_name};'
            )
            assert content.endswith(expected_ending), \
                f"Extended language should end with case alias: {expected_ending}"

    def test_file_has_no_syntax_errors(self, language_file):
        """Test basic JavaScript syntax validity."""
        content = language_file.read_text()

        # Check braces are balanced
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, "Unbalanced braces"

        # Check brackets are balanced
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        assert open_brackets == close_brackets, "Unbalanced brackets"

        # Note: We don't check parentheses balance because regex patterns
        # include non-capturing groups (?:, lookaheads (?=, etc. that make
        # simple counting inaccurate


class TestLanguageSpecificPatterns:
    """Test language-specific patterns in generated files."""

    def test_zolo_has_root_key_pattern(self, bundle_dir):
        """Test generic zolo has root-key pattern."""
        content = (bundle_dir / 'prism-zolo.js').read_text()
        assert "'root-key':" in content or '"root-key":' in content
        assert 'class-name' in content  # Root keys should be class-name alias

    def test_zspark_root_highlighting_parked(self, bundle_dir):
        """zSpark semantic highlighting is parked (being rebuilt from scratch).

        The generated file must NOT contain the old zspark-root/zspark-nested
        patterns; it inherits everything from base zolo.
        """
        content = (bundle_dir / 'prism-zspark.js').read_text()
        assert "'zspark-root':" not in content and '"zspark-root":' not in content
        assert "'zspark-nested':" not in content and '"zspark-nested":' not in content
        assert "Prism.languages.extend('zolo'," in content

    def test_zspark_has_zpath_value_pattern(self, bundle_dir):
        """Test zspark keeps the zPath value override (only remaining override)."""
        content = (bundle_dir / 'prism-zspark.js').read_text()
        assert "'zspark-zpath-value':" in content or '"zspark-zpath-value":' in content
        # zPath values only apply after specific keys (zScrapath = deprecated alias)
        assert 'zLogPath' in content
        assert 'zScrapath' in content
        assert 'zVaFolder' in content
        assert 'zSpace' in content

    def test_zui_has_special_root_pattern(self, bundle_dir):
        """Test zui has special root patterns."""
        content = (bundle_dir / 'prism-zui.js').read_text()
        assert "'zui-special-root':" in content or '"zui-special-root":' in content
        assert 'zMeta' in content or 'zVaF' in content

    def test_zui_has_element_pattern(self, bundle_dir):
        """Test zui has UI element patterns."""
        content = (bundle_dir / 'prism-zui.js').read_text()
        assert "'zui-element':" in content or '"zui-element":' in content

    def test_zui_has_element_property_pattern(self, bundle_dir):
        """Test zui has UI element property patterns."""
        content = (bundle_dir / 'prism-zui.js').read_text()
        assert "'zui-element-property':" in content or '"zui-element-property":' in content

    def test_zschema_has_zmeta_root_pattern(self, bundle_dir):
        """Test zschema has zMeta root pattern."""
        content = (bundle_dir / 'prism-zschema.js').read_text()
        assert "'zschema-zmeta-root':" in content or '"zschema-zmeta-root":' in content
        assert 'zMeta' in content

    def test_zschema_has_property_pattern(self, bundle_dir):
        """Test zschema has field property patterns."""
        content = (bundle_dir / 'prism-zschema.js').read_text()
        assert "'zschema-property':" in content or '"zschema-property":' in content

    def test_zconfig_has_special_root_pattern(self, bundle_dir):
        """Test zconfig has special root patterns."""
        content = (bundle_dir / 'prism-zconfig.js').read_text()
        assert "'zconfig-special-root':" in content or '"zconfig-special-root":' in content
        assert 'zMachine' in content

    def test_zconfig_has_section_patterns(self, bundle_dir):
        """Test zconfig has section header patterns."""
        content = (bundle_dir / 'prism-zconfig.js').read_text()
        assert "'zmachine-locked-section':" in content or '"zmachine-locked-section":' in content
        assert "'zmachine-editable-section':" in content or '"zmachine-editable-section":' in content

    def test_zenv_has_config_root_pattern(self, bundle_dir):
        """Test zenv has config root patterns."""
        content = (bundle_dir / 'prism-zenv.js').read_text()
        assert "'zenv-config-root':" in content or '"zenv-config-root":' in content

    def test_zenv_has_znavbar_pattern(self, bundle_dir):
        """Test zenv has ZNAVBAR nested patterns."""
        content = (bundle_dir / 'prism-zenv.js').read_text()
        assert "'znavbar-nested':" in content or '"znavbar-nested":' in content

    def test_zenv_has_zpath_pattern(self, bundle_dir):
        """Test zenv has zPath value patterns."""
        content = (bundle_dir / 'prism-zenv.js').read_text()
        assert "'zpath-value':" in content or '"zpath-value":' in content


class TestPatternOrdering:
    """Test that patterns are in correct order."""

    @pytest.fixture(params=ALL_LANGUAGES)
    def language_file(self, bundle_dir, request):
        language_name = request.param
        return bundle_dir / f'prism-{language_name}.js'

    def test_comment_comes_first(self, language_file):
        """Test that comment pattern comes first (in base or inherited)."""
        content = language_file.read_text()

        is_base = 'Prism.languages.zolo = {' in content
        is_extended = "Prism.languages.extend('zolo'," in content

        if is_base:
            # Base zolo should have comment explicitly first
            comment_pos = content.find("'comment':")
            if comment_pos == -1:
                comment_pos = content.find('"comment":')

            lang_def_pos = content.find('Prism.languages.')
            assert comment_pos > lang_def_pos, "Comment should be first pattern in base"
        elif is_extended:
            # Extended languages inherit comment from base zolo
            assert "Prism.languages.extend('zolo'," in content
        else:
            pytest.fail("File doesn't match base or extended pattern structure")

    def test_colon_comes_last(self, language_file):
        """Test that colon (punctuation) pattern comes last in base."""
        content = language_file.read_text()

        is_base = 'Prism.languages.zolo = {' in content
        is_extended = "Prism.languages.extend('zolo'," in content

        if is_base:
            # Base zolo should have colon explicitly last. Nested 'inside'
            # blocks (array/object) also define 'colon', so take the last
            # occurrence — that's the top-level pattern.
            colon_pos = content.rfind("'colon':")
            if colon_pos == -1:
                colon_pos = content.rfind('"colon":')
            assert colon_pos != -1, "Base should define 'colon' pattern"

            closing_pos = content.rfind('};')

            # Colon should be near the end (before closing brace)
            assert colon_pos < closing_pos, "Colon should be last pattern in base"
            assert closing_pos - colon_pos < 200, "Colon should be close to end"
        elif is_extended:
            # Extended languages inherit colon/punctuation from base zolo
            assert "Prism.languages.extend('zolo'," in content
        else:
            pytest.fail("File doesn't match base or extended pattern structure")


class TestRegression:
    """Regression tests for specific bugs."""

    def test_settings_page_bug_fixed(self, bundle_dir):
        """
        Regression test: Settings_Page should be colored as root-key.

        This was the original bug that started the generator project.
        """
        content = (bundle_dir / 'prism-zolo.js').read_text()

        # Check that root-key pattern exists
        assert "'root-key':" in content or '"root-key":' in content

        # Check that it matches any case (lowercase or Capital)
        assert '[a-zA-Z]' in content

        # Check that it has column 0 detection (capturing or non-capturing group)
        assert ('(^|' in content or '(?:^|' in content or '(?<=\\n)' in content), \
            "Root key pattern must match at column 0"
