from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from private_ai_infra.cli import main
from private_ai_infra.ollama import OllamaUnavailable


class CliTests(unittest.TestCase):
    def test_init_dry_run_and_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dry-run"

            init_code = main(
                [
                    "init",
                    "--dry-run",
                    "--mode",
                    "local-developer",
                    "--project-name",
                    "demo",
                    "--company-name",
                    "acme",
                    "--output-dir",
                    str(output),
                ]
            )
            validate_code = main(["validate", str(output)])

            self.assertEqual(init_code, 0)
            self.assertEqual(validate_code, 0)
            self.assertTrue((output / "architecture-plan.md").exists())

    def test_apply_is_not_implemented(self):
        self.assertEqual(main(["apply"]), 2)

    def test_init_without_dry_run_is_blocked(self):
        self.assertEqual(main(["init"]), 2)

    def test_modes_command(self):
        self.assertEqual(main(["modes"]), 0)

    def test_ingest_and_chat_retrieval_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "api.md").write_text("APIs require authentication and authorization checks.", encoding="utf-8")
            index_dir = root / "index"

            ingest_code = main(["ingest", str(docs), "--output-dir", str(index_dir)])
            chat_code = main(["chat", "authorization checks", "--index", str(index_dir / "index.json")])

            self.assertEqual(ingest_code, 0)
            self.assertEqual(chat_code, 0)

    def test_chat_with_ollama_returns_answer_and_retrieval_citations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "policy.md").write_text(
                "Approved AI tools may use only data that is allowed for that tool.",
                encoding="utf-8",
            )
            index_dir = root / "index"
            self.assertEqual(main(["ingest", str(docs), "--output-dir", str(index_dir)]), 0)

            output = StringIO()
            with patch("private_ai_infra.cli.OllamaClient") as client_type:
                client_type.return_value.generate_grounded_answer.return_value = (
                    "Employees may use approved AI tools only with allowed data [1]."
                )
                with redirect_stdout(output):
                    code = main(
                        [
                            "chat",
                            "What are the AI usage rules?",
                            "--index",
                            str(index_dir / "index.json"),
                            "--model",
                            "test-model",
                        ]
                    )

            self.assertEqual(code, 0)
            self.assertIn("Local model RAG response", output.getvalue())
            self.assertIn("allowed data [1]", output.getvalue())
            self.assertIn("policy.md#chunk-0", output.getvalue())

    def test_chat_refuses_unsupported_question_without_calling_ollama(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "policy.md").write_text(
                "Approved AI tools require documented authorization. "
                "If requested behavior is not present, the assistant must refuse.",
                encoding="utf-8",
            )
            index_dir = root / "index"
            self.assertEqual(main(["ingest", str(docs), "--output-dir", str(index_dir)]), 0)

            output = StringIO()
            with patch("private_ai_infra.cli.OllamaClient") as client_type:
                with redirect_stdout(output):
                    code = main(
                        [
                            "chat",
                            "What minerals are present on the moon?",
                            "--index",
                            str(index_dir / "index.json"),
                            "--model",
                            "test-model",
                        ]
                    )

            self.assertEqual(code, 0)
            self.assertIn("Local RAG refusal", output.getvalue())
            client_type.assert_not_called()

    def test_chat_uses_retrieval_fallback_when_ollama_is_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "policy.md").write_text(
                "Approved AI tools require documented authorization.",
                encoding="utf-8",
            )
            index_dir = root / "index"
            self.assertEqual(main(["ingest", str(docs), "--output-dir", str(index_dir)]), 0)

            output = StringIO()
            errors = StringIO()
            with patch("private_ai_infra.cli.OllamaClient") as client_type:
                client_type.return_value.generate_grounded_answer.side_effect = OllamaUnavailable(
                    "local Ollama is unavailable"
                )
                with redirect_stdout(output), redirect_stderr(errors):
                    code = main(
                        [
                            "chat",
                            "What authorization is required?",
                            "--index",
                            str(index_dir / "index.json"),
                            "--model",
                            "test-model",
                        ]
                    )

            self.assertEqual(code, 0)
            self.assertIn("Retrieval-only response", output.getvalue())
            self.assertIn("retrieval-only fallback", errors.getvalue())

    def test_chat_rejects_unbounded_top_k(self):
        errors = StringIO()
        with redirect_stderr(errors):
            code = main(["chat", "question", "--top-k", "100"])

        self.assertEqual(code, 2)
        self.assertIn("--top-k must be between 1 and 10", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
