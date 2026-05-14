"""Test runner module for zlsp CLI."""


def run_tests(args):
    """Run zlsp tests using pytest."""
    try:
        import pytest  # type: ignore # pylint: disable=import-outside-toplevel
    except ImportError:
        print("[ERROR] pytest not installed. Install with: pip install pytest")
        return 1

    # Build pytest arguments
    pytest_args = ["-v"]

    # Determine which tests to run
    test_dir = "tests"
    if args.unit:
        test_dir = "tests/unit"
        print("Running unit tests...")
    elif args.integration:
        test_dir = "tests/integration"
        print("Running integration tests...")
    elif args.e2e:
        test_dir = "tests/e2e"
        print("Running end-to-end tests...")
    elif args.quick:
        # Quick mode: unit + integration only (skip slow tests)
        pytest_args.extend(["-m", "not slow"])
        print("Running quick tests (unit + integration)...")
        print("   Skipping: e2e tests (slow)")
    else:
        # Full mode: all tests including visual
        print("Running FULL test suite...")
        print("   ├─ Unit tests")
        print("   ├─ Integration tests")
        print("   ├─ End-to-end tests")

    pytest_args.append(test_dir)

    # Add coverage if requested
    if args.coverage:
        pytest_args.extend(["--cov=core", "--cov-report=term-missing", "--cov-report=html"])
        print("Coverage reporting enabled (terminal + HTML)")

    # Add verbose flag
    if args.verbose:
        pytest_args.append("-vv")

    # Add specific test if provided
    if args.test:
        pytest_args.append("-k")
        pytest_args.append(args.test)
        print(f"Running test: {args.test}")

    # Fail fast (stop on first failure)
    if args.failfast:
        pytest_args.append("-x")
        print("Fail-fast enabled (stop on first failure)")

    print(f"\nRunning: pytest {' '.join(pytest_args)}\n")

    # Run pytest
    return pytest.main(pytest_args)
