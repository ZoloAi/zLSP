"""
Multi-Language Prism.js Generator

Generates Prism.js syntax highlighting definitions for all zolo file types.
Extracts patterns from zlsp SSOT (KeyDetector, TokenRegistry, FileTypeDetector).

Usage:
    python3 -m zlsp.generators.generate_prism_zolo

Output (single committed bundle — manual handoff, no auto-deploy):
    - zLSP/bifrost-prism/prism-zolo.js (generic)
    - zLSP/bifrost-prism/prism-zspark.js
    - zLSP/bifrost-prism/prism-zui.js
    - zLSP/bifrost-prism/prism-zschema.js
    - zLSP/bifrost-prism/prism-zconfig.js
    - zLSP/bifrost-prism/prism-zenv.js

A dev copies the bundle into the bifrost client (zbifrost-client/syntax/),
then pushes + bumps that repo. This generator never writes into other repos.
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
    """Ensure the local bifrost-prism bundle dir exists and return it.

    This is the SINGLE committed output. No cross-repo deployment — a dev copies
    the bundle to zbifrost-client/syntax/ manually, then pushes + bumps.
    """
    bundle_dir = project_root / 'bifrost-prism'
    bundle_dir.mkdir(exist_ok=True)
    return bundle_dir


def generate_base_language_file(bundle_dir: Path) -> Path:
    """
    Generate the base zolo language file.
    
    Args:
        bundle_dir: Output directory (zLSP/bifrost-prism/)
        
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
        bundle_dir: Output directory (zLSP/bifrost-prism/)
        
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
    print("Manual handoff (no auto-deploy):")
    print("  1. Copy zLSP/bifrost-prism/* → zbifrost-client/syntax/")
    print("  2. Push + bump zbifrost-client, then update the CDN pin")


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
