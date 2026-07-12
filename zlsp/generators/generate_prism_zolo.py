"""
Multi-Language Prism.js Generator

Generates Prism.js syntax highlighting definitions for all zolo file types.
Extracts patterns from zlsp SSOT (KeyDetector, TokenRegistry, FileTypeDetector).

Usage:
    python3 -m zlsp.generators.generate_prism_zolo

Output (single committed bundle, shipped as PACKAGE DATA in the wheel):
    - zlsp/generated/prism-zolo.js (generic)
    - zlsp/generated/prism-zspark.js
    - zlsp/generated/prism-zui.js
    - zlsp/generated/prism-zschema.js
    - zlsp/generated/prism-zconfig.js
    - zlsp/generated/prism-zenv.js

No manual handoff anymore: zOS.zServer serves this directory straight from
the installed package via zlsp.bifrost_prism_dir() (mounted at
/zsyntax/<version>/ and announced as `syntaxBase` in zui-config), so deployed
highlighting always matches THIS package's grammar. Regenerate + commit
whenever the grammar SSOT changes; test_prism_patterns.py fails on a stale
bundle. This generator never writes into other repos.
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


def ensure_bundle_dir() -> Path:
    """Ensure the packaged bundle dir (zlsp/generated/) exists and return it.

    This is the SINGLE committed output AND what ships in the wheel — it must
    live inside the zlsp package so bifrost_prism_dir() can serve it from any
    install. (The old repo-root bifrost-prism/ + manual copy into
    zbifrost-client is retired; the client's bundled syntax/ is a frozen
    fallback for pre-/zsyntax/ servers only.)
    """
    bundle_dir = project_root / 'zlsp' / 'generated'
    bundle_dir.mkdir(exist_ok=True)
    return bundle_dir


def generate_base_language_file(bundle_dir: Path) -> Path:
    """
    Generate the base zolo language file.
    
    Args:
        bundle_dir: Output directory (zlsp/generated/)
        
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
    output_file = bundle_dir / 'prism-zolo.js'
    output_file.write_text(js_content, encoding='utf-8')
    print(f"  - Written to {output_file}")
    
    return output_file


def generate_extended_language_file(
    file_type: FileType,
    config: Dict[str, Any],
    base_patterns: List[Dict[str, Any]],
    bundle_dir: Path
) -> Path:
    """
    Generate an extended Prism language file that inherits from base zolo.
    
    Args:
        file_type: The file type to generate
        config: Language configuration
        base_patterns: Base zolo patterns (for reference)
        bundle_dir: Output directory (zlsp/generated/)
        
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
    output_file = bundle_dir / f'prism-{name}.js'
    output_file.write_text(js_content, encoding='utf-8')
    print(f"  - Written to {output_file}")
    
    return output_file


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
    
    # Ensure the single committed bundle dir exists
    bundle_dir = ensure_bundle_dir()
    print(f"Output bundle: {bundle_dir}")
    print()
    
    # Generate base zolo language first
    base_file = generate_base_language_file(bundle_dir)
    base_patterns = generate_base_patterns()
    generated_files = [base_file]
    print()
    
    # Get language configurations (excluding GENERIC since we already generated base)
    configs = generate_language_configs()
    file_types = [ft for ft in get_all_file_types() if ft != FileType.GENERIC]
    
    # Generate specialized languages that extend base zolo
    for file_type in file_types:
        config = configs[file_type]
        output_file = generate_extended_language_file(file_type, config, base_patterns, bundle_dir)
        generated_files.append(output_file)
        print()
    
    # Summary
    print("=" * 60)
    print("Generation complete!")
    print("=" * 60)
    print(f"Generated {len(generated_files)} language files in {bundle_dir}/:")
    for file_type in file_types:
        config = configs[file_type]
        print(f"  - {config['name']}: {config['description']}")
    print()
    print("Bundle ships as package data (zlsp/generated/) — commit it with the")
    print("grammar change; zOS serves it at /zsyntax/<version>/ automatically.")


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
