"""Info display module for zlsp CLI."""

import os


def show_info(args):  # pylint: disable=unused-argument
    """Show zlsp information."""
    from zlsp.version import __version__  # pylint: disable=import-outside-toplevel

    print("╔═══════════════════════════════════════╗")
    print("║   Zolo Language Server Protocol      ║")
    print("╚═══════════════════════════════════════╝")
    print(f"\nVersion: {__version__}")
    print(f"Installation: {os.path.dirname(os.path.dirname(__file__))}")
    print("\nFeatures:")
    print("  • String-first philosophy")
    print("  • Semantic token highlighting")
    print("  • Real-time diagnostics")
    print("  • Code completion")
    print("  • Hover information")
    print("\nCommands:")
    print("  zlsp verify            - Verify installation health")
    print("  zlsp test              - Run all tests (full suite)")
    print("  zlsp test --quick      - Run quick tests (unit + integration)")
    print("  zlsp test --unit       - Run unit tests only")
    print("  zlsp test --integration - Run integration tests (includes semantic token snapshots)")
    print("  zlsp test --e2e        - Run end-to-end tests only")
    print("  zlsp test --coverage   - Run with coverage report")
    print("  zlsp server            - Start LSP server")
    print("  zlsp info              - Show this information")
    print("\nMore info: https://github.com/ZoloAi/ZoloMedia/tree/main/zlsp")
