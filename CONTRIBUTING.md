# Contributing

Contributions are welcome when they keep the project small, safe, and testable.

1. Fork the repository and create a focused branch.
2. Use Python 3.10+ and install with `python -m pip install -e .`.
3. Run `python -m unittest discover -s tests -v` and `python -m compileall -q src tests`.
4. Add tests for behavior changes and update both README language sections when user-facing behavior changes.
5. Never commit real MCP credentials, tokens, private endpoints, or user configuration files.
6. Open a pull request describing the problem, approach, and validation performed.

Please keep validation deterministic. The inspector must not execute commands or make network requests while examining a configuration.
