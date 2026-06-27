import tempfile
import unittest
from pathlib import Path

from private_ai_infra.indexer import build_index
from private_ai_infra.retrieval import format_retrieval_answer, search_index


class IndexerRetrievalTests(unittest.TestCase):
    def test_build_index_and_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "policy.md").write_text(
                "Remote work requires manager approval and approved company storage.",
                encoding="utf-8",
            )
            (docs / ".env").write_text("SECRET=bad", encoding="utf-8")

            result = build_index([docs], output_dir=root / "index", collection="policies")
            matches = search_index(result.index_path, "remote work approval")
            answer = format_retrieval_answer("remote work approval", matches)

            self.assertEqual(result.files_indexed, 1)
            self.assertEqual(result.chunks_indexed, 1)
            self.assertTrue(any("denied pattern .env" in skipped for skipped in result.skipped_files))
            self.assertEqual(matches[0]["source_name"], "policy.md")
            self.assertIn("Retrieval-only response", answer)
            self.assertIn("policy.md", answer)

    def test_denied_files_are_excluded_from_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "safe.md").write_text("Approved public test content.", encoding="utf-8")
            (docs / ".env").write_text("PASSWORD=do-not-index", encoding="utf-8")
            (docs / "id_rsa").write_text("private-key-material", encoding="utf-8")
            (docs / "credentials.json").write_text('{"token": "do-not-index"}', encoding="utf-8")

            result = build_index([docs], output_dir=root / "index", collection="docs")
            payload = result.index_path.read_text(encoding="utf-8")

            self.assertEqual(result.files_indexed, 1)
            self.assertEqual(result.chunks_indexed, 1)
            self.assertIn("safe.md", payload)
            self.assertNotIn("do-not-index", payload)
            self.assertNotIn("private-key-material", payload)
            self.assertEqual(len(result.skipped_files), 3)

    def test_search_ignores_stop_word_only_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "unrelated.md").write_text(
                "The approved process is documented here.",
                encoding="utf-8",
            )
            result = build_index([docs], output_dir=root / "index", collection="docs")

            matches = search_index(result.index_path, "What minerals are present on the moon?")

            self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
