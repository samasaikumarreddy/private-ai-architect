import json
import tempfile
import unittest
from pathlib import Path

from private_ai_infra.evaluation import evaluate_index
from private_ai_infra.indexer import build_index


class EvaluationTests(unittest.TestCase):
    def test_evaluation_checks_retrieval_and_refusal_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "policy.md").write_text(
                "AI usage rules require approved tools and allowed data.",
                encoding="utf-8",
            )
            index = build_index([docs], output_dir=root / "index", collection="docs")
            cases_path = root / "cases.json"
            cases_path.write_text(
                json.dumps(
                    {
                        "cases": [
                            {
                                "id": "supported-policy",
                                "query": "What are the AI usage rules?",
                                "should_retrieve": True,
                                "expected_sources": ["policy.md"],
                            },
                            {
                                "id": "unsupported-moon",
                                "query": "What minerals are present on the moon?",
                                "should_retrieve": False,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            report = evaluate_index(index.index_path, cases_path)

            self.assertTrue(report.ok)
            self.assertEqual(report.passed, 2)
            self.assertIn("Passed: 2/2", report.to_text())

    def test_evaluation_rejects_duplicate_case_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index_path = root / "index.json"
            index_path.write_text('{"entries": []}', encoding="utf-8")
            cases_path = root / "cases.json"
            cases_path.write_text(
                '{"cases": [{"id": "same", "query": "one"}, {"id": "same", "query": "two"}]}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Duplicate evaluation case id"):
                evaluate_index(index_path, cases_path)


if __name__ == "__main__":
    unittest.main()
