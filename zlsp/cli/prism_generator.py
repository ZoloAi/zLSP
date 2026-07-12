"""
Prism.js generation CLI command.

Generates Prism.js syntax highlighting files from zlsp SSOT.
"""


def generate_prism_patterns(args):
    """
    Generate Prism.js language patterns from parser SSOT.
    
    Generates 6 language-specific files:
    - prism-zolo.js (generic)
    - prism-zspark.js
    - prism-zui.js
    - prism-zschema.js
    - prism-zconfig.js
    - prism-zenv.js
    """
    print("=" * 70)
    print("Generating Prism.js Patterns (from Parser SSOT)")
    print("=" * 70)
    print()
    
    try:
        # Import and run the generator
        from zlsp.generators.generate_prism_zolo import generate_all_languages
        generate_all_languages()
        return 0
    except Exception as e:
        print(f"✗ Error generating Prism patterns: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def generate_prism_css(args):
    """
    Generate Prism.js CSS theme from zlsp color theme.
    
    Generates:
    - prism-zolo-theme.css
    """
    print("=" * 70)
    print("Generating Prism.js CSS Theme (from Theme YAML)")
    print("=" * 70)
    print()
    
    try:
        # Import and run the CSS generator
        from zlsp.themes.generators.prism import generate_prism_css_theme
        css_path = generate_prism_css_theme()
        print()
        print(f"✅ Generated CSS: {css_path}")
        print()
        return 0
    except Exception as e:
        print(f"✗ Error generating Prism CSS: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def generate_prism_all(args):
    """
    Generate both Prism.js patterns and CSS theme.
    
    This is the default/recommended command that generates everything.
    """
    print("=" * 70)
    print("Generating Prism.js (Patterns + CSS)")
    print("=" * 70)
    print()
    
    # Generate patterns first
    patterns_result = generate_prism_patterns(args)
    print()
    
    # Generate CSS
    css_result = generate_prism_css(args)
    print()
    
    # Summary
    if patterns_result == 0 and css_result == 0:
        print("=" * 70)
        print("✅ Prism.js generation complete!")
        print("=" * 70)
        print()
        print("Generated bundle: zlsp/generated/ (ships as package data)")
        print("  - prism-*.js (6 pattern files)")
        print("  - prism-zolo-theme.css")
        print()
        print("Commit the bundle with the grammar change — zOS serves it at")
        print("/zsyntax/<version>/ straight from the installed package.")
        print()
        return 0
    else:
        print("=" * 70)
        print("✗ Prism.js generation failed")
        print("=" * 70)
        return 1


def run_prism_generation(args):
    """Route to appropriate Prism generation handler."""
    if args.css_only:
        return generate_prism_css(args)
    elif args.patterns_only:
        return generate_prism_patterns(args)
    else:
        # Default: generate both
        return generate_prism_all(args)


def standalone_generate_prism():
    """
    Standalone entry point for zlsp-generate-prism command.
    
    This is used by pyproject.toml for the CLI command.
    """
    import argparse
    
    # Create minimal args object
    parser = argparse.ArgumentParser(
        description="Generate Prism.js syntax highlighting files"
    )
    parser.add_argument("--patterns-only", action="store_true",
                       help="Generate only JS patterns")
    parser.add_argument("--css-only", action="store_true",
                       help="Generate only CSS theme")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    return run_prism_generation(args)
