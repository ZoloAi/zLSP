"""Argument parser configuration for zlsp CLI."""

import argparse

from zlsp.cli.test_runner import run_tests
from zlsp.cli.server_runner import start_server
from zlsp.cli.info_display import show_info
from zlsp.cli.health_check import run_health_check
from zlsp.cli.prism_generator import run_prism_generation


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="zlsp",
        description="Zolo Language Server Protocol - Testing and Server CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zlsp verify                # Verify installation
  zlsp verify --verbose      # Detailed health check
  zlsp test                  # Run all tests (full suite)
  zlsp test --quick          # Quick tests (unit + integration + snapshots)
  zlsp test --unit           # Unit tests only
  zlsp test --integration    # Integration tests (includes semantic token snapshots)
  zlsp test --e2e            # End-to-end tests only
  zlsp test --coverage       # Run with coverage report
  zlsp test -k test_parser   # Run specific test
  zlsp test -x               # Stop on first failure
  zlsp server                # Start LSP server
  zlsp info                  # Show information
  zlsp generate-prism        # Generate Prism.js patterns + CSS
  zlsp generate-prism --patterns-only  # Generate JS patterns only
  zlsp generate-prism --css-only       # Generate CSS theme only

For more information: https://github.com/ZoloAi/ZoloMedia/tree/main/zlsp
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--unit", action="store_true",
                            help="Run only unit tests (fast)")
    test_parser.add_argument("--integration", action="store_true",
                            help="Run only integration tests")
    test_parser.add_argument("--e2e", action="store_true",
                            help="Run only end-to-end tests (slow)")
    test_parser.add_argument("--quick", action="store_true",
                            help="Run quick tests (unit + integration, skip slow)")
    test_parser.add_argument("--coverage", action="store_true",
                            help="Generate coverage report")
    test_parser.add_argument("-v", "--verbose", action="store_true",
                            help="Verbose output")
    test_parser.add_argument("-k", "--test", help="Run specific test by name")
    test_parser.add_argument("-x", "--failfast", action="store_true",
                            help="Stop on first test failure")
    test_parser.set_defaults(func=run_tests)

    # Server command
    server_parser = subparsers.add_parser("server", help="Start LSP server")
    server_parser.set_defaults(func=start_server)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show zlsp information")
    info_parser.set_defaults(func=show_info)

    # Health check / verify command
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify zlsp installation and health"
    )
    verify_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed checks")
    verify_parser.set_defaults(func=run_health_check)

    # Generate Prism.js command
    generate_parser = subparsers.add_parser(
        "generate-prism",
        help="Generate Prism.js syntax highlighting files"
    )
    generate_parser.add_argument(
        "--patterns-only",
        action="store_true",
        help="Generate only JS patterns (from parser SSOT)"
    )
    generate_parser.add_argument(
        "--css-only",
        action="store_true",
        help="Generate only CSS theme (from theme YAML)"
    )
    generate_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output with stack traces"
    )
    generate_parser.set_defaults(func=run_prism_generation)

    return parser
