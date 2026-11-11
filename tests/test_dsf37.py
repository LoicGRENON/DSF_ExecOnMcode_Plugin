"""Backend regression checks against the real DSF 3.7 client, without a printer."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

BACKEND = Path(__file__).resolve().parents[1] / "src" / "dsf"
sys.dont_write_bytecode = True
sys.path.insert(0, str(BACKEND))
import dsf
from dsf.commands.code import Code
from MCodeAction import MCodeAction
from compat import enum_value, resolved_path, major_number, MCODE, SUCCESS

spec = importlib.util.spec_from_file_location("exec_on_mcode", BACKEND / "execOnMcode.py")
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)


class Dsf37Tests(unittest.TestCase):
    def test_linux_entrypoint_has_a_valid_shebang(self):
        source = (BACKEND / "execOnMcode.py").read_bytes()
        self.assertEqual(source.split(b"\n")[0], b"#!/usr/bin/python3")
        self.assertNotIn(b"\r\n", source)

    def test_real_protocol_supported(self):
        self.assertGreaterEqual(dsf.PROTOCOL_VERSION, 12)

    def test_legacy_and_current_client_api_shapes(self):
        self.assertEqual(enum_value(SimpleNamespace(Success=0), "SUCCESS", "Success"), 0)
        self.assertEqual(enum_value(SimpleNamespace(SUCCESS=0), "SUCCESS", "Success"), 0)
        self.assertEqual(resolved_path("/config.json"), "/config.json")
        self.assertEqual(resolved_path(SimpleNamespace(result="/config.json")), "/config.json")
        self.assertEqual(major_number(SimpleNamespace(majorNumber=1200)), 1200)
        self.assertEqual(major_number(SimpleNamespace(major_number=1200)), 1200)

    def test_resolve_path_returns_string_and_existing_config_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "ExecOnMcode.json"
            contents = json.dumps([{"cmd_code": "M1215", "cmd_command": "echo existing", "cmd_timeout": 0}])
            config.write_text(contents)
            backend.cmd_conn = Mock(resolve_path=Mock(return_value=str(config)))
            actions = backend.get_actions_from_config()
            self.assertEqual(actions[0].cmd_code, "M1215")
            self.assertIsNone(actions[0].cmd_timeout)
            self.assertEqual(config.read_text(), contents)

    def test_missing_config_is_created_using_resolved_path(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "nested" / "ExecOnMcode.json"
            backend.cmd_conn = Mock(resolve_path=Mock(return_value=str(config)))
            actions = backend.get_actions_from_config()
            self.assertTrue(config.is_file())
            self.assertEqual([action.cmd_code for action in actions], ["M1201", "M1202"])

    def test_intercepted_code_uses_current_code_type_and_result(self):
        code = Code.from_json({"command": "Code", "type": "M", "majorNumber": 1201, "result": None, "parameters": []})
        self.assertEqual(code.type, MCODE)
        self.assertEqual(major_number(code), 1201)
        action = MCodeAction({"cmd_code": "M1201", "cmd_command": "echo example"})
        connection = Mock()
        with patch.object(backend.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "example", "")) as run:
            getattr(backend, "__do_action_for_code")(connection, [action], code)
        run.assert_called_once_with("echo example", shell=True, timeout=30, capture_output=True, text=True)
        connection.resolve_code.assert_called_once_with(SUCCESS, "[ExecOnMcode]: example")

    def test_disabled_code_never_runs(self):
        code = Code.from_json({"command": "Code", "type": "M", "majorNumber": 1201, "result": None, "parameters": []})
        action = MCodeAction({"cmd_code": "M1201", "cmd_command": "echo example", "cmd_enabled": False})
        connection = Mock()
        with patch.object(backend.subprocess, "run") as run:
            getattr(backend, "__do_action_for_code")(connection, [action], code)
        run.assert_not_called()
        connection.ignore_code.assert_called_once()


if __name__ == "__main__":
    unittest.main()
