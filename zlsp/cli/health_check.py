"""Health check module for zlsp CLI."""

import os
import sys
import traceback


def run_health_check(args):  # pylint: disable=too-many-locals
    """Run health check to verify zlsp installation."""
    verbose = args.verbose if hasattr(args, 'verbose') else False

    print("╔═══════════════════════════════════════╗")
    print("║   zlsp Health Check                  ║")
    print("╚═══════════════════════════════════════╝\n")

    issues = []
    checks_passed = 0
    total_checks = 0

    # Check 1: Python version
    total_checks += 1
    print("Checking Python version...")
    if sys.version_info >= (3, 8):
        v = sys.version_info
        print(f"   [ok] Python {v.major}.{v.minor}.{v.micro} (OK)")
        checks_passed += 1
    else:
        print(f"   [ERROR] Python {sys.version_info.major}.{sys.version_info.minor} (requires 3.8+)")
        issues.append("Python version too old (need 3.8+)")

    # Check 2: Core dependencies
    total_checks += 1
    print("\nChecking dependencies...")
    try:
        import pygls  # type: ignore # pylint: disable=import-outside-toplevel
        import lsprotocol  # type: ignore # pylint: disable=import-outside-toplevel

        # Get versions safely
        pygls_version = getattr(pygls, '__version__', 'installed')
        lsprotocol_version = getattr(lsprotocol, '__version__', 'installed')

        print(f"   [ok] pygls {pygls_version} (OK)")
        print(f"   [ok] lsprotocol {lsprotocol_version} (OK)")
        checks_passed += 1
    except ImportError as e:
        print(f"   [ERROR] Missing dependency: {e}")
        issues.append(f"Missing dependency: {e}")

    # Check 3: Parser functionality
    total_checks += 1
    print("\nTesting parser...")
    try:
        from zlsp.parser.parser_service import loads  # pylint: disable=import-outside-toplevel
        from zlsp.parser.parser import dumps  # pylint: disable=import-outside-toplevel

        # Test basic parsing
        test_data = "name: Zolo\nversion(int): 1"
        result = loads(test_data)

        if result == {"name": "Zolo", "version": 1}:
            print("   [ok] Parser loads() working")
        else:
            print(f"   [ERROR] Parser returned unexpected result: {result}")
            issues.append("Parser loads() returned unexpected result")

        # Test dump
        dumped = dumps(result)
        if "name:" in dumped and "version" in dumped:
            print("   [ok] Parser dumps() working")
        else:
            print("   [ERROR] Parser dumps() failed")
            issues.append("Parser dumps() failed")

        checks_passed += 1
    except Exception as e:  # pylint: disable=broad-except
        print(f"   [ERROR] Parser test failed: {e}")
        issues.append(f"Parser error: {e}")
        if verbose:
            traceback.print_exc()

    # Check 4: LSP server availability
    total_checks += 1
    print("\nChecking LSP server...")
    try:
        from zlsp.server.lsp_server import ZoloLanguageServer  # pylint: disable=import-outside-toplevel,unused-import
        print("   [ok] LSP server module available")
        checks_passed += 1
    except Exception as e:  # pylint: disable=broad-except
        print(f"   [ERROR] LSP server unavailable: {e}")
        issues.append(f"LSP server error: {e}")
        if verbose:
            traceback.print_exc()

    # Check 5: Semantic tokenizer
    total_checks += 1
    print("\nChecking semantic tokenizer...")
    try:
        from zlsp.server.semantic_tokenizer import encode_semantic_tokens  # pylint: disable=import-outside-toplevel
        from zlsp.parser.parser_service import tokenize  # pylint: disable=import-outside-toplevel

        # Tokenize test content
        test_content = "test: value"
        parse_result = tokenize(test_content)

        # Test encoding the tokens
        encoded = encode_semantic_tokens(parse_result.tokens)

        # As long as it runs without crashing and returns something, it's working
        if encoded is not None:
            print("   [ok] Semantic tokenizer working")
            checks_passed += 1
        else:
            print("   [ERROR] Semantic tokenizer returned None")
            issues.append("Semantic tokenizer returned None")
    except Exception as e:  # pylint: disable=broad-except
        print(f"   [ERROR] Semantic tokenizer failed: {e}")
        issues.append(f"Semantic tokenizer error: {e}")
        if verbose:
            traceback.print_exc()

    # Check 6: Editor integrations (optional)
    print("\nChecking editor integrations...")
    editors_installed = []

    # Check Vim
    vim_config = os.path.expanduser("~/.vim/pack/zolo/start/zlsp")
    if os.path.exists(vim_config):
        editors_installed.append("Vim")

    # Check Neovim  # cspell:ignore nvim
    nvim_config = os.path.expanduser("~/.config/nvim/pack/zolo/start/zlsp")
    if os.path.exists(nvim_config):
        editors_installed.append("Neovim")

    # Check VSCode
    vscode_ext = os.path.expanduser("~/.vscode/extensions/zolo-lsp-1.0.0")
    if os.path.exists(vscode_ext):
        editors_installed.append("VSCode")

    # Check Cursor
    cursor_ext = os.path.expanduser("~/.cursor/extensions/zolo-lsp-1.0.0")
    if os.path.exists(cursor_ext):
        editors_installed.append("Cursor")

    if editors_installed:
        print(f"   [ok] Installed for: {', '.join(editors_installed)}")
    else:
        print("   [INFO] No editor integrations detected (run zlsp-install-[editor])")

    # Check 7: Example files (verbose mode)
    if verbose:
        total_checks += 1
        print("\nChecking example files...")
        try:
            # Try to find examples directory
            zlsp_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            examples_path = os.path.join(zlsp_root, 'examples')
            if os.path.exists(examples_path):
                examples = [f for f in os.listdir(examples_path) if f.endswith('.zolo')]
                print(f"   [ok] Found {len(examples)} example files")
                checks_passed += 1
            else:
                print("   [INFO] Example files not found (normal for pip install)")
        except Exception as e:  # pylint: disable=broad-except
            print(f"   [INFO] Could not check examples: {e}")

    # Summary
    print("\n" + "="*42)
    print("Health Check Summary")
    print("="*42)
    print(f"   Checks passed: {checks_passed}/{total_checks}")

    if issues:
        print(f"\n[ERROR] Issues found ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print("\nSuggested fixes:")
        print("   • Reinstall: pip uninstall zlsp && pip install zlsp")
        print("   • Check Python version: python --version")
        print("   • Install dependencies: pip install pygls lsprotocol")
        return 1
    else:
        print("\n[OK] All checks passed! zlsp is working correctly.")
        print("\nNext steps:")
        if not editors_installed:
            print("   • Install for your editor:")
            print("     - zlsp-install-vim")
            print("     - zlsp-install-vscode")
            print("     - zlsp-install-cursor")
        print("   • Try: zolo-lsp (starts LSP server)")
        print("   • Docs: https://github.com/ZoloAi/ZoloMedia/tree/main/zlsp")
        return 0
