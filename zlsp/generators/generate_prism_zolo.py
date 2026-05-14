"""
Multi-Language Prism.js Generator

Generates Prism.js syntax highlighting definitions for all zolo file types.
Extracts patterns from zlsp SSOT (KeyDetector, TokenRegistry, FileTypeDetector).

Usage:
    python3 -m zlsp.generators.generate_prism_zolo

Output:
    - zlsp/generated/prism-zolo.js (generic)
    - zlsp/generated/prism-zspark.js
    - zlsp/generated/prism-zui.js
    - zlsp/generated/prism-zschema.js
    - zlsp/generated/prism-zconfig.js
    - zlsp/generated/prism-zenv.js
    - Copies all 6 files to zOS/bifrost/src/syntax/
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add zlsp to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from zlsp.parser.zvaf.file_type_detector import FileType
from zlsp.generators.prism_pattern_generator import (
    generate_base_patterns,
    generate_override_patterns_for_file_type,
    generate_language_configs,
    build_prism_base_language,
    build_prism_extended_language,
)
from zlsp.generators.file_type_pattern_extractor import get_all_file_types


def ensure_directories_exist():
    """Ensure output directories exist."""
    # Generated files directory (zlsp project root is project_root, so generated/ is direct child)
    generated_dir = project_root / 'generated'
    generated_dir.mkdir(exist_ok=True)
    
    # Bifrost syntax directory (in parent of zlsp project)
    bifrost_syntax_dir = project_root.parent / 'zOS' / 'bifrost' / 'src' / 'syntax'
    bifrost_syntax_dir.mkdir(parents=True, exist_ok=True)
    
    # zCloud static JS directory (for runtime loading - this is where /static/ is served from)
    static_js_dir = project_root.parent / 'zCloud' / 'static' / 'js'
    static_js_dir.mkdir(parents=True, exist_ok=True)
    
    return generated_dir, bifrost_syntax_dir, static_js_dir


def generate_base_language_file(generated_dir: Path) -> Path:
    """
    Generate the base zolo language file.
    
    Args:
        generated_dir: Output directory
        
    Returns:
        Path to generated prism-zolo.js
    """
    print("Generating base zolo language...")
    
    # Generate base patterns
    patterns = generate_base_patterns()
    print(f"  - {len(patterns)} base patterns")
    
    # Build JavaScript
    js_content = build_prism_base_language(patterns)
    
    # Write to file
    output_file = generated_dir / 'prism-zolo.js'
    output_file.write_text(js_content, encoding='utf-8')
    print(f"  - Written to {output_file}")
    
    return output_file


def generate_extended_language_file(
    file_type: FileType,
    config: Dict[str, Any],
    base_patterns: List[Dict[str, Any]],
    generated_dir: Path
) -> Path:
    """
    Generate an extended Prism language file that inherits from base zolo.
    
    Args:
        file_type: The file type to generate
        config: Language configuration
        base_patterns: Base zolo patterns (for reference)
        generated_dir: Output directory
        
    Returns:
        Path to generated file
    """
    name = config['name']
    description = config['description']
    
    print(f"Generating {name} language (extends zolo)...")
    
    # Generate override patterns
    override_patterns = generate_override_patterns_for_file_type(file_type)
    print(f"  - {len(override_patterns)} override patterns")
    
    # Build JavaScript
    js_content = build_prism_extended_language(name, base_patterns, override_patterns, description)
    
    # Write to file
    output_file = generated_dir / f'prism-{name}.js'
    output_file.write_text(js_content, encoding='utf-8')
    print(f"  - Written to {output_file}")
    
    return output_file


def copy_to_deployment_dirs(source_file: Path, bifrost_syntax_dir: Path, static_js_dir: Path):
    """
    Copy generated file to deployment directories.
    
    Args:
        source_file: Source file in zlsp/generated/
        bifrost_syntax_dir: Destination directory in zOS/bifrost/src/syntax/ (dev reference)
        static_js_dir: Destination directory in zCloud/static/js/ (runtime loading)
    """
    # Copy to bifrost/src/syntax (for development reference)
    dest_syntax = bifrost_syntax_dir / source_file.name
    dest_syntax.write_text(source_file.read_text(encoding='utf-8'), encoding='utf-8')
    print(f"  - Copied to {dest_syntax}")
    
    # Copy to zCloud/static/js (for runtime loading via /static/ route)
    dest_static = static_js_dir / source_file.name
    dest_static.write_text(source_file.read_text(encoding='utf-8'), encoding='utf-8')
    print(f"  - Copied to {dest_static}")


def generate_all_languages():
    """
    Generate all 6 Prism language definitions.
    
    Generates:
    - prism-zolo.js (generic)
    - prism-zspark.js
    - prism-zui.js
    - prism-zschema.js
    - prism-zconfig.js
    - prism-zenv.js
    """
    print("=" * 60)
    print("Multi-Language Prism.js Generator")
    print("=" * 60)
    print()
    
    # Ensure directories exist
    generated_dir, bifrost_syntax_dir, static_js_dir = ensure_directories_exist()
    print(f"Output directory: {generated_dir}")
    print(f"Bifrost syntax directory: {bifrost_syntax_dir}")
    print(f"Static JS directory (runtime): {static_js_dir}")
    print()
    
    # Generate base zolo language first
    base_file = generate_base_language_file(generated_dir)
    base_patterns = generate_base_patterns()
    generated_files = [base_file]
    print()
    
    # Get language configurations (excluding GENERIC since we already generated base)
    configs = generate_language_configs()
    file_types = [ft for ft in get_all_file_types() if ft != FileType.GENERIC]
    
    # Generate specialized languages that extend base zolo
    for file_type in file_types:
        config = configs[file_type]
        output_file = generate_extended_language_file(file_type, config, base_patterns, generated_dir)
        generated_files.append(output_file)
        print()
    
    # Copy to deployment directories
    print("Copying to deployment directories...")
    for source_file in generated_files:
        copy_to_deployment_dirs(source_file, bifrost_syntax_dir, static_js_dir)
    print()
    
    # Summary
    print("=" * 60)
    print("Generation complete!")
    print("=" * 60)
    print(f"Generated {len(generated_files)} language files:")
    for file_type in file_types:
        config = configs[file_type]
        print(f"  - {config['name']}: {config['description']}")
    print()
    print("Files written to:")
    print(f"  - {generated_dir}/ (canonical)")
    print(f"  - {bifrost_syntax_dir}/ (dev reference)")
    print(f"  - {static_js_dir}/ (runtime /static/ route)")
    print()
    print("Next steps:")
    print("  1. Run tests: python3 -m pytest zlsp/tests/")
    print("  2. Open browser test: zlsp/tests/browser/test_all_languages.html")
    print("  3. Update documentation with language-specific code fences")


def main():
    """Main entry point."""
    try:
        generate_all_languages()
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
