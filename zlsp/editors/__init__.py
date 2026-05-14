"""
Editor integrations for zlsp.

Each editor has its own subfolder with installation scripts and configuration.
"""
import sys


def install_all():
    """Install zlsp for all supported editors and generate Prism.js files."""
    from zlsp.editors.vim.install import main as vim_install
    from zlsp.editors.vscode.install import main as vscode_install
    from zlsp.editors.cursor.install import main as cursor_install
    from zlsp.cli.prism_generator import generate_prism_all
    
    print("Installing zlsp for all supported editors + web highlighting...\n")
    
    editors = [
        ("Vim", vim_install),
        ("VSCode", vscode_install),
        ("Cursor", cursor_install),
    ]
    
    results = {}
    
    # Install editor integrations
    for name, install_func in editors:
        print(f"\n{'='*60}")
        print(f"Installing for {name}...")
        print('='*60)
        try:
            exit_code = install_func()
            results[name] = exit_code == 0
        except Exception as e:
            print(f"✗ Error installing for {name}: {e}")
            results[name] = False
    
    # Generate Prism.js files for web
    print(f"\n{'='*60}")
    print("Generating Prism.js (Web Syntax Highlighting)...")
    print('='*60)
    try:
        # Create minimal args object for generate_prism_all
        class Args:
            verbose = False
        
        exit_code = generate_prism_all(Args())
        results["Prism.js"] = exit_code == 0
    except Exception as e:
        print(f"✗ Error generating Prism.js: {e}")
        results["Prism.js"] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("Installation Summary:")
    print('='*60)
    for name, success in results.items():
        status = "[ok] Success" if success else "✗ Failed"
        print(f"  {name}: {status}")
    
    # Exit with non-zero if any failed
    if not all(results.values()):
        sys.exit(1)
    print("\n[ok] All installations completed successfully!")
    print("\nNext steps:")
    print("  1. Restart your editor(s)")
    print("  2. Restart zServer (if using web UI)")
    print("  3. Open a .zolo file to see syntax highlighting")
    sys.exit(0)


def uninstall_all():
    """Uninstall zlsp from all supported editors."""
    from zlsp.editors.vim.uninstall import main as vim_uninstall
    from zlsp.editors.vscode.uninstall import main as vscode_uninstall
    from zlsp.editors.cursor.uninstall import main as cursor_uninstall
    
    print("Uninstalling zlsp from all supported editors...\n")
    
    editors = [
        ("Vim", vim_uninstall),
        ("VSCode", vscode_uninstall),
        ("Cursor", cursor_uninstall),
    ]
    
    results = {}
    for name, uninstall_func in editors:
        print(f"\n{'='*60}")
        print(f"Uninstalling from {name}...")
        print('='*60)
        try:
            exit_code = uninstall_func()
            results[name] = exit_code == 0
        except Exception as e:
            print(f"✗ Error uninstalling from {name}: {e}")
            results[name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("Uninstallation Summary:")
    print('='*60)
    for name, success in results.items():
        status = "[ok] Success" if success else "✗ Failed"
        print(f"  {name}: {status}")
    
    # Exit with non-zero if any failed
    if not all(results.values()):
        sys.exit(1)
    print("\n[ok] All uninstallations completed successfully!")
    sys.exit(0)
