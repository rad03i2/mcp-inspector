from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import ConfigError, inspect_config, load_config, redacted_config, summary

VERSION = "1.0.0"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mcp-inspector-local", description="Inspect MCP client configuration safely without starting servers.")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = p.add_subparsers(dest="action", required=True)
    for name, help_text in (("check", "Validate configuration and report findings"), ("summary", "Show a safe server inventory"), ("redact", "Print or save a copy with likely secrets redacted")):
        s = sub.add_parser(name, help=help_text)
        s.add_argument("config", type=Path)
        s.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
        if name == "redact":
            s.add_argument("--output", type=Path, help="Write redacted JSON to this path")
    return p


def _text_report(data: dict) -> str:
    lines = [f"MCP servers: {data['server_count']}"]
    for item in data["servers"]:
        state = "disabled" if item["disabled"] else "enabled"
        lines.append(f"- {item['name']}: {item['transport']} ({state})")
    c = data["finding_counts"]
    lines.append(f"Findings: {c['error']} error(s), {c['warning']} warning(s), {c['info']} info")
    for f in data["findings"]:
        lines.append(f"[{f['level'].upper()}] {f['server']} {f['code']}: {f['message']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        config = load_config(args.config)
        if args.action == "redact":
            result = redacted_config(config)
            rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
            if args.output:
                if args.output.resolve() == args.config.resolve():
                    raise ConfigError("Refusing to overwrite the source configuration")
                args.output.write_text(rendered, encoding="utf-8")
                print(str(args.output))
            else:
                print(rendered, end="")
            return 0
        data = summary(config)
        if args.action == "summary":
            # Summary still includes findings but never environment values.
            pass
        print(json.dumps(data, indent=2, ensure_ascii=False) if args.json else _text_report(data))
        return 1 if any(f.level == "error" for f in inspect_config(config)) else 0
    except (ConfigError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
