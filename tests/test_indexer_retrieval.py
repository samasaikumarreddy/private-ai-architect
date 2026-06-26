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


if __name__ == "__main__":
    unittest.main()

