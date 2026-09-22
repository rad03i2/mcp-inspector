# Security Policy

## Scope
MCP Inspector Local parses configuration files but **never starts MCP servers, executes configured commands, or contacts configured URLs**. This separation is intentional.

## Sensitive configuration
Configuration files can contain credentials. Prefer environment-variable indirection. The `summary` and `check` commands expose environment variable names but never their values. `redact` replaces values for likely secret environment keys and common authentication headers; heuristic redaction is not a substitute for secret scanning.

Do not publish a configuration merely because `redact` produced a copy. Review it first, especially custom headers or unusually named credential fields.

## Reporting
Please report security concerns privately through GitHub's security-reporting facilities when available. Do not open a public issue containing credentials or exploit details.
