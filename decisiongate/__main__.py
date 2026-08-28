"""Allow ``python -m decisiongate`` to invoke the CLI."""

from decisiongate.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
