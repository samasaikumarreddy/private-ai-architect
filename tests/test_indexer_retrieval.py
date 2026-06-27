import tempfile
import unittest
import json
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

    def test_source_code_ingestion_prunes_generated_and_sensitive_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            (project / "src").mkdir(parents=True)
            (project / "build").mkdir()
            (project / ".gradle").mkdir()
            (project / "autoeq_upstream").mkdir()
            (project / "src" / "MainActivity.kt").write_text(
                "class MainActivity { fun applyEqProfile() = Unit }",
                encoding="utf-8",
            )
            (project / "src" / "service.py").write_text(
                "def detect_song(): return 'approved'",
                encoding="utf-8",
            )
            (project / "build" / "Generated.kt").write_text("generated-secret", encoding="utf-8")
            (project / ".gradle" / "cache.txt").write_text("cache-secret", encoding="utf-8")
            (project / "autoeq_upstream" / "dataset.txt").write_text("vendor-data", encoding="utf-8")
            (project / "upload-keystore.jks").write_text("key-material", encoding="utf-8")
            (project / "google-services.json").write_text('{"api_key": "secret"}', encoding="utf-8")

            result = build_index(
                [project],
                output_dir=root / "index",
                collection="code",
                exclude_patterns=("autoeq_upstream",),
            )
            payload = result.index_path.read_text(encoding="utf-8")

            self.assertEqual(result.files_indexed, 2)
            self.assertIn("MainActivity.kt", payload)
            self.assertIn("service.py", payload)
            self.assertNotIn("generated-secret", payload)
            self.assertNotIn("cache-secret", payload)
            self.assertNotIn("vendor-data", payload)
            self.assertNotIn("key-material", payload)
            self.assertNotIn('"api_key"', payload)
            self.assertTrue(any("denied directory build" in item for item in result.skipped_files))
            self.assertTrue(any("user exclusion pattern" in item for item in result.skipped_files))
            self.assertTrue(any("denied pattern *.jks" in item for item in result.skipped_files))
            self.assertTrue(any("denied pattern google-services.json" in item for item in result.skipped_files))

    def test_bm25_prefers_chunk_covering_specific_query_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "generic.md").write_text(
                "The architecture review defines team ownership and planning.",
                encoding="utf-8",
            )
            (docs / "android.md").write_text(
                "Android NotificationListenerService detects songs. "
                "AudioEffect applies EQ profiles.",
                encoding="utf-8",
            )
            result = build_index([docs], output_dir=root / "index", collection="docs")

            matches = search_index(
                result.index_path,
                "Which Android components detect songs and apply EQ profiles?",
            )

            self.assertEqual(matches[0]["source_name"], "android.md")
            self.assertEqual(len(matches), 1)
            self.assertGreater(float(matches[0]["score"]), 0)

    def test_search_reads_v0_2_index_without_frequency_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            index_path = Path(tmp) / "index.json"
            index_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "source_path": "policy.md",
                                "source_name": "policy.md",
                                "chunk_index": 0,
                                "text": "Remote work requires manager approval.",
                                "terms": ["approval", "manager", "remote", "requires", "work"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            matches = search_index(index_path, "remote work approval")

            self.assertEqual(matches[0]["source_name"], "policy.md")

    def test_index_file_count_limit_stops_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            for index in range(3):
                (docs / f"{index}.md").write_text(f"document {index}", encoding="utf-8")

            result = build_index([docs], output_dir=root / "index", collection="docs", max_files=2)

            self.assertEqual(result.files_indexed, 2)
            self.assertIn("index file limit reached: 2", result.skipped_files)

    def test_denied_name_above_approved_source_does_not_block_ingestion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            approved = root / "tmp" / "approved"
            approved.mkdir(parents=True)
            (approved / "README.md").write_text("approved content", encoding="utf-8")

            result = build_index([approved], output_dir=root / "index", collection="docs")

            self.assertEqual(result.files_indexed, 1)
            self.assertIn("approved content", result.index_path.read_text(encoding="utf-8"))

    def test_output_directory_inside_source_is_pruned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "project"
            output = source / "generated" / "index"
            output.mkdir(parents=True)
            (source / "README.md").write_text("approved project overview", encoding="utf-8")
            (output / "old-index.json").write_text('{"text": "must-not-reingest"}', encoding="utf-8")

            result = build_index([source], output_dir=output, collection="code", force=True)
            payload = result.index_path.read_text(encoding="utf-8")

            self.assertEqual(result.files_indexed, 1)
            self.assertNotIn("must-not-reingest", payload)
            self.assertTrue(any("generated output directory" in item for item in result.skipped_files))


if __name__ == "__main__":
    unittest.main()
