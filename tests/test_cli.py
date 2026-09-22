import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from mcp_inspector.cli import main


class CLITests(unittest.TestCase):
    def _config(self, root: str, data: dict) -> Path:
        p = Path(root) / "mcp.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        return p

    def test_check_valid_returns_zero(self):
        with TemporaryDirectory() as tmp, redirect_stdout(StringIO()):
            p = self._config(tmp, {"mcpServers": {"x": {"command": "python"}}})
            self.assertEqual(main(["check", str(p)]), 0)

    def test_check_invalid_returns_one(self):
        with TemporaryDirectory() as tmp, redirect_stdout(StringIO()):
            p = self._config(tmp, {"mcpServers": {"x": {}}})
            self.assertEqual(main(["check", str(p)]), 1)

    def test_redact_refuses_source_overwrite(self):
        with TemporaryDirectory() as tmp, redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            p = self._config(tmp, {"mcpServers": {}})
            self.assertEqual(main(["redact", str(p), "--output", str(p)]), 2)

    def test_redact_writes_safe_copy(self):
        with TemporaryDirectory() as tmp, redirect_stdout(StringIO()):
            p = self._config(tmp, {"mcpServers": {"x": {"command": "x", "env": {"API_KEY": "abc"}}}})
            out = Path(tmp) / "safe.json"
            self.assertEqual(main(["redact", str(p), "--output", str(out)]), 0)
            self.assertNotIn("abc", out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
