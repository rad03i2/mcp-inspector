import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mcp_inspector.core import ConfigError, inspect_config, load_config, redacted_config, summary


class InspectorTests(unittest.TestCase):
    def test_valid_stdio_server(self):
        cfg = {"mcpServers": {"tools": {"command": "python", "args": ["-m", "tools"], "env": {"MODE": "safe"}}}}
        self.assertFalse([f for f in inspect_config(cfg) if f.level == "error"])
        self.assertEqual(summary(cfg)["servers"][0]["transport"], "stdio")

    def test_transport_is_exclusive(self):
        cfg = {"mcpServers": {"bad": {"command": "x", "url": "https://example.test"}}}
        self.assertIn("transport", [f.code for f in inspect_config(cfg)])

    def test_remote_http_warns(self):
        cfg = {"mcpServers": {"remote": {"url": "http://example.test/mcp"}}}
        self.assertIn("insecure_http", [f.code for f in inspect_config(cfg)])

    def test_local_http_does_not_warn(self):
        cfg = {"mcpServers": {"local": {"url": "http://localhost:8000/mcp"}}}
        self.assertNotIn("insecure_http", [f.code for f in inspect_config(cfg)])

    def test_embedded_secret_warning_and_redaction(self):
        cfg = {"mcpServers": {"x": {"command": "x", "env": {"API_TOKEN": "do-not-print"}, "headers": {"Authorization": "Bearer hidden"}}}}
        self.assertIn("embedded_secret", [f.code for f in inspect_config(cfg)])
        safe = redacted_config(cfg)
        encoded = json.dumps(safe)
        self.assertNotIn("do-not-print", encoded)
        self.assertNotIn("Bearer hidden", encoded)

    def test_summary_never_contains_env_values(self):
        cfg = {"mcpServers": {"x": {"command": "x", "env": {"MODE": "private-value"}}}}
        self.assertNotIn("private-value", json.dumps(summary(cfg)))

    def test_invalid_args_and_env(self):
        cfg = {"mcpServers": {"x": {"command": "x", "args": "oops", "env": []}}}
        codes = {f.code for f in inspect_config(cfg)}
        self.assertTrue({"args", "env"}.issubset(codes))

    def test_load_errors_are_clear(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.json"
            p.write_text("{", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(p)

    def test_missing_servers(self):
        with self.assertRaises(ConfigError):
            inspect_config({})


if __name__ == "__main__":
    unittest.main()
