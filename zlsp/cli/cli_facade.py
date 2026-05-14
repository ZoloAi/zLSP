"""
CLI facade for zlsp - Language Server and test runner.

Commands:
    zlsp test         # Run tests
    zlsp test --unit  # Run unit tests only
    zlsp server       # Start LSP server
"""

import sys

from zlsp.cli.argument_parser import create_parser
from zlsp.cli.test_runner import run_tests
from zlsp.cli.server_runner import start_server
from zlsp.cli.info_display import show_info
from zlsp.cli.health_check import run_health_check
from zlsp.cli.prism_generator import run_prism_generation


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Route to appropriate handler
    if args.command == "test":
        sys.exit(run_tests(args))
    elif args.command == "server":
        start_server(args)
    elif args.command == "info":
        show_info(args)
    elif args.command == "verify":
        sys.exit(run_health_check(args))
    elif args.command == "generate-prism":
        sys.exit(run_prism_generation(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
