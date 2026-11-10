import importlib.util
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("doubao_runtime", BASE / "scripts/runtime.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
build_spec = importlib.util.spec_from_file_location("doubao_build", BASE / "build.py")
builder = importlib.util.module_from_spec(build_spec)
build_spec.loader.exec_module(builder)

PREDICTION = "# 测试\n\n**Platform**: unknown\n\n## 预测 v1\n\n判断：先试一次。\n\n## 推理因素\n\n来自稿件。\n"


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.project = Path(self.directory.name)

    def file(self, relative, content):
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write(self, content):
        return runtime.write_prediction(self.project, "predictions/a.md", content)

    def test_new_prediction_and_retro_preserve_exact_original(self):
        self.write(PREDICTION)
        self.write(PREDICTION + "\n## 复盘\n数据待收集。\n")
        self.assertEqual(runtime.protect(self.project)["protected_files"], 1)
        self.assertEqual(runtime.read_text(self.project / "predictions/a.md"), PREDICTION + "\n## 复盘\n数据待收集。\n")

    def test_rewrite_prediction_rejected_without_modifying_file(self):
        self.write(PREDICTION)
        with self.assertRaises(runtime.BridgeError):
            self.write(PREDICTION.replace("先试一次", "必定大爆"))
        self.assertEqual(runtime.read_text(self.project / "predictions/a.md"), PREDICTION)

    def test_header_change_allowed(self):
        self.write(PREDICTION)
        self.write(PREDICTION.replace("unknown", "douyin"))
        self.assertIn("douyin", runtime.read_text(self.project / "predictions/a.md"))

    def test_v2_append_is_protected_independently(self):
        self.write(PREDICTION)
        second = PREDICTION + "\n## 预测 v2\n拍后新判断。\n\n## 复盘\n"
        self.assertEqual(self.write(second)["protected_sections"], 2)
        with self.assertRaises(runtime.BridgeError):
            self.write(second.replace("拍后新判断", "篡改判断"))

    def test_prediction_deletion_rejected(self):
        self.write(PREDICTION)
        with self.assertRaises(runtime.BridgeError):
            self.write("# 没有预测段\n")

    def test_external_edit_and_deleted_file_detected(self):
        self.write(PREDICTION)
        target = self.project / "predictions/a.md"
        target.write_text("# 直接篡改\n")
        with self.assertRaises(runtime.BridgeError):
            runtime.protect(self.project)
        target.unlink()
        with self.assertRaises(runtime.BridgeError):
            runtime.check_ledger(self.project, runtime.load_ledger(self.project))

    def test_external_prediction_edit_cannot_be_rebaselined(self):
        self.write(PREDICTION)
        self.file("predictions/a.md", PREDICTION.replace("先试一次", "改过了"))
        with self.assertRaises(runtime.BridgeError):
            runtime.protect(self.project)

    def test_reordered_prediction_versions_rejected(self):
        first = "## 预测 v1\nA\n"
        second = "## 预测 v2\nB\n"
        self.write(first + second)
        with self.assertRaises(runtime.BridgeError):
            self.write(second + first)

    def test_markdown_example_heading_not_real_prediction(self):
        self.assertEqual(runtime.prediction_sections("```md\n## 预测\n假的\n```\n"), [])
        text = "## 预测\n```md\n## 示例\n```\n仍在预测内\n## 复盘\n结果\n"
        self.assertIn("仍在预测内", runtime.prediction_sections(text)[0])
        self.assertNotIn("结果", runtime.prediction_sections(text)[0])

    def test_symlink_and_path_traversal_rejected(self):
        for relative in ("../escape.md", "/tmp/escape.md"):
            with self.assertRaises(runtime.BridgeError):
                runtime.project_path(self.project, relative)
        (self.project / "predictions").symlink_to(self.project, target_is_directory=True)
        with self.assertRaises(runtime.BridgeError):
            self.write(PREDICTION)

    def test_blind_input_excludes_actuals_and_primary_history(self):
        self.file("scripts/a.md", "正文只有一次经历。")
        self.file("rubric_notes.md", "ER 情绪清晰度。")
        self.file("audience.md", "不允许传给盲评的画像")
        self.file("rubric-memo.md", "不允许传给盲评的实绩")
        self.file(".cheat-state.json", '{"secret_context":"不允许传给盲评的状态"}')
        inputs = runtime.blind_input(self.project, "scripts/a.md")
        payload = json.dumps(inputs, ensure_ascii=False)
        self.assertEqual(set(inputs), {"script_path", "rubric_notes_path", "script", "rubric_notes"})
        self.assertNotIn("不允许传给盲评", payload)
        for relative in ("audience.md", "videos/a/script.md", "scripts/../../outside.md"):
            with self.assertRaises(runtime.BridgeError):
                runtime.blind_input(self.project, relative)

    def valid_score(self):
        inputs = {"script_path": "scripts/a.md", "script": "这是稿件", "rubric_notes": "composite = (ER) / 1 * 2"}
        result = {"script_path": "scripts/a.md", "script_hash": "sha256:" + hashlib.sha256(inputs["script"].encode()).hexdigest()[:12],
                  "dimensions": {"ER": {"score": 3, "confidence": "medium", "reason": "具体经历"}},
                  "refusal": None, "input_status": {"script_read": True, "rubric_notes_read": True, "any_other_file_read": False},
                  "self_check": {field: False for field in ("saw_play_numbers", "saw_comments", "saw_retro_segment", "any_contamination_signal")}}
        return result, inputs

    def test_blind_response_validation(self):
        result, inputs = self.valid_score()
        self.assertEqual(runtime.validate_blind(result, inputs), result)
        for score in (-1, 6, True, "3"):
            result["dimensions"]["ER"]["score"] = score
            with self.assertRaises(runtime.BridgeError):
                runtime.validate_blind(result, inputs)

    def test_original_non_blind_warning_is_preserved_without_claiming_clean(self):
        result, inputs = self.valid_score()
        result["refusal"] = "non_blind_warning"
        result["self_check"]["any_contamination_signal"] = True
        returned = runtime.validate_blind(result, inputs)
        self.assertEqual(returned["refusal"], "non_blind_warning")
        self.assertTrue(returned["self_check"]["any_contamination_signal"])
        result["dimensions"]["ER"]["confidence"] = "high"
        with self.assertRaises(runtime.BridgeError):
            runtime.validate_blind(result, inputs)

    def test_http_request_has_only_new_messages_and_key_only_in_header(self):
        observed = {}
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return json.dumps({"choices": [{"message": {"content": '{"ok":true}'}}]}).encode()
        class Opener:
            def open(self, request, timeout):
                observed["request"] = request
                return Response()
        with patch.object(runtime, "build_opener", return_value=Opener()):
            result = runtime.chat({"endpoint": "https://example.com/chat/completions", "model": "m", "api_key": "only-in-header"}, "scorer-rules", "two-account-inputs")
        self.assertTrue(result["ok"])
        request = observed["request"]
        payload = json.loads(request.data)
        self.assertEqual(payload["messages"], [{"role": "system", "content": "scorer-rules"}, {"role": "user", "content": "two-account-inputs"}])
        self.assertNotIn("only-in-header", request.data.decode())
        self.assertEqual(request.get_header("Authorization"), "Bearer only-in-header")

    def test_blind_hash_and_contamination_rejected(self):
        result, inputs = self.valid_score()
        result["script_hash"] = "wrong"
        with self.assertRaises(runtime.BridgeError):
            runtime.validate_blind(result, inputs)

    def test_missing_or_extra_dimensions_rejected(self):
        result, inputs = self.valid_score()
        inputs["rubric_notes"] = "composite = (ER + HP + QL + NA + AB + SR + SAT) / 7 * 2"
        with self.assertRaises(runtime.BridgeError):
            runtime.validate_blind(result, inputs)
        inputs["rubric_notes"] = "composite = (ER) / 1 * 2"
        result["dimensions"]["UNKNOWN"] = {"score": 1, "confidence": "low", "reason": "无依据"}
        with self.assertRaises(runtime.BridgeError):
            runtime.validate_blind(result, inputs)
        result, inputs = self.valid_score()
        result["self_check"]["any_contamination_signal"] = True
        with self.assertRaises(runtime.BridgeError):
            runtime.validate_blind(result, inputs)

    def test_unconfigured_models_do_not_call_network(self):
        with patch.object(runtime, "chat") as call:
            with self.assertRaises(runtime.BridgeError):
                runtime.blind_score(self.project, "scripts/a.md")
            call.assert_not_called()

    def test_same_model_cannot_be_cross_model_audit(self):
        with patch.object(runtime, "config", return_value={"model": "same-model"}):
            with self.assertRaises(runtime.BridgeError):
                runtime.audit(self.project, {})

    def test_audit_preserves_rejection_and_rejects_insufficient_reason(self):
        request = {"old_formula": "old", "new_formula": "new", "samples": [{"id": "a"}], "ranking": {}}
        configs = [{"model": "doubao"}, {"model": "qwen"}]
        rejected = {"verdict": "REJECT", "reason": "证据不足，不能通过。" * 20, "risks": []}
        with patch.object(runtime, "config", side_effect=configs), patch.object(runtime, "chat", return_value=rejected):
            self.assertEqual(runtime.audit(self.project, request)["verdict"], "REJECT")
        with patch.object(runtime, "config", side_effect=configs), patch.object(runtime, "chat", return_value={"verdict": "PASS", "reason": "可以"}):
            with self.assertRaises(runtime.BridgeError):
                runtime.audit(self.project, request)

    def test_model_endpoint_rejects_credentials_query_and_http(self):
        for endpoint in ("http://example.com/chat", "https://key@example.com/chat", "https://example.com/chat?api_key=x"):
            self.file(".cheat-secrets.json", json.dumps({"doubao_bridge": {"blind": {"endpoint": endpoint, "model": "m", "api_key": "never-print"}}}))
            with self.assertRaises(runtime.BridgeError):
                runtime.config(self.project, "blind")

    def test_package_allowlist_excludes_credentials_and_caches(self):
        self.file("SKILL.md", "skill")
        for name in builder.TOP_FILES:
            self.file(name, "source")
        self.file("adapters/perf-data/example/crawler.py", "# source")
        self.file("adapters/perf-data/example/.auth/session.json", "secret")
        self.file("adapters/perf-data/example/__pycache__/cached.py", "cache")
        self.file(".cheat-secrets.json", "secret")
        self.file("predictions/personal.md", "private")
        with patch.object(builder, "ROOT", self.project):
            files = [p.relative_to(self.project).as_posix() for p in builder.original_files()]
        self.assertIn("adapters/perf-data/example/crawler.py", files)
        self.assertFalse(any(".auth" in path or "cached" in path or "personal" in path or "secrets" in path for path in files))


if __name__ == "__main__":
    unittest.main()
