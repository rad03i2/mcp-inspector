"""Pure validation and inspection logic for MCP client configuration files."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

SAFE_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SECRET_HINTS = ("token", "secret", "password", "passwd", "api_key", "apikey", "private_key")


class ConfigError(ValueError):
    """Raised when an MCP configuration cannot be parsed or validated."""


@dataclass(frozen=True)
class Finding:
    level: str
    server: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise ConfigError(f"Configuration file not found: {source}")
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ConfigError("Configuration must be UTF-8 JSON") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ConfigError("Top-level configuration must be a JSON object")
    return data


def _servers(config: dict[str, Any]) -> dict[str, Any]:
    servers = config.get("mcpServers")
    if servers is None:
        raise ConfigError("Missing required 'mcpServers' object")
    if not isinstance(servers, dict):
        raise ConfigError("'mcpServers' must be an object")
    return servers


def inspect_config(config: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    servers = _servers(config)
    if not servers:
        findings.append(Finding("warning", "*", "empty", "No MCP servers are configured"))
        return findings

    for name, spec in sorted(servers.items()):
        if not isinstance(name, str) or not name.strip():
            findings.append(Finding("error", str(name), "name", "Server name must be a non-empty string"))
            continue
        if not isinstance(spec, dict):
            findings.append(Finding("error", name, "server_type", "Server definition must be an object"))
            continue

        command = spec.get("command")
        url = spec.get("url")
        if bool(command) == bool(url):
            findings.append(Finding("error", name, "transport", "Define exactly one of 'command' or 'url'"))
        if command is not None and (not isinstance(command, str) or not command.strip()):
            findings.append(Finding("error", name, "command", "'command' must be a non-empty string"))
        if url is not None:
            if not isinstance(url, str) or not url.startswith(("http://", "https://")):
                findings.append(Finding("error", name, "url", "'url' must start with http:// or https://"))
            elif url.startswith("http://") and not url.startswith(("http://localhost", "http://127.0.0.1", "http://[::1]")):
                findings.append(Finding("warning", name, "insecure_http", "Remote HTTP transport is not encrypted; prefer HTTPS"))

        args = spec.get("args", [])
        if not isinstance(args, list) or any(not isinstance(item, str) for item in args):
            findings.append(Finding("error", name, "args", "'args' must be an array of strings"))

        env = spec.get("env", {})
        if not isinstance(env, dict):
            findings.append(Finding("error", name, "env", "'env' must be an object"))
        else:
            for key, value in env.items():
                if not isinstance(key, str) or not SAFE_ENV_NAME.fullmatch(key):
                    findings.append(Finding("error", name, "env_name", f"Invalid environment variable name: {key!r}"))
                    continue
                if not isinstance(value, str):
                    findings.append(Finding("error", name, "env_value", f"Environment variable {key} must be a string"))
                low = key.lower()
                if any(hint in low for hint in SECRET_HINTS) and isinstance(value, str) and value and not value.startswith(("${", "$env:", "env:")):
                    findings.append(Finding("warning", name, "embedded_secret", f"{key} appears to contain an inline secret; prefer environment indirection"))

        unknown = sorted(set(spec) - {"command", "args", "env", "cwd", "url", "headers", "disabled"})
        for key in unknown:
            findings.append(Finding("info", name, "unknown_key", f"Unrecognized key retained for client compatibility: {key}"))
    return findings


def summary(config: dict[str, Any]) -> dict[str, Any]:
    servers = _servers(config)
    findings = inspect_config(config)
    counts = {level: sum(f.level == level for f in findings) for level in ("error", "warning", "info")}
    items = []
    for name, spec in sorted(servers.items()):
        if isinstance(spec, dict):
            transport = "stdio" if spec.get("command") else "http" if spec.get("url") else "invalid"
            items.append({"name": name, "transport": transport, "disabled": bool(spec.get("disabled", False)), "args_count": len(spec.get("args", [])) if isinstance(spec.get("args", []), list) else None, "env_names": sorted(spec.get("env", {}).keys()) if isinstance(spec.get("env", {}), dict) else []})
        else:
            items.append({"name": name, "transport": "invalid", "disabled": False, "args_count": None, "env_names": []})
    return {"server_count": len(servers), "servers": items, "finding_counts": counts, "findings": [f.to_dict() for f in findings]}


def redacted_config(config: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy with likely inline secrets replaced by <redacted>."""
    clone = json.loads(json.dumps(config))
    servers = clone.get("mcpServers", {})
    if isinstance(servers, dict):
        for spec in servers.values():
            if not isinstance(spec, dict):
                continue
            env = spec.get("env")
            if isinstance(env, dict):
                for key in list(env):
                    if isinstance(key, str) and any(h in key.lower() for h in SECRET_HINTS):
                        env[key] = "<redacted>"
            headers = spec.get("headers")
            if isinstance(headers, dict):
                for key in list(headers):
                    if str(key).lower() in {"authorization", "proxy-authorization", "x-api-key"}:
                        headers[key] = "<redacted>"
    return clone
