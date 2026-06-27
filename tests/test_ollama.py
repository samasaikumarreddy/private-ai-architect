import unittest

from private_ai_infra.ollama import (
    OllamaClient,
    OllamaModelUnavailable,
    validate_local_model_name,
    validate_local_ollama_url,
)


class OllamaClientTests(unittest.TestCase):
    def test_generate_preflights_installed_model_and_uses_only_context(self):
        calls = []

        def fake_request(url, method, payload, timeout):
            calls.append((url, method, payload, timeout))
            if url.endswith("/api/tags"):
                return {"models": [{"name": "test-model:latest", "model": "test-model:latest"}]}
            return {
                "message": {
                    "role": "assistant",
                    "content": "Approved AI tools may use only allowed data [1].",
                }
            }

        client = OllamaClient(request_json=fake_request)
        answer = client.generate_grounded_answer(
            "What are the AI usage rules?",
            [
                {
                    "source_path": "policy.md",
                    "chunk_index": 0,
                    "text": "Approved AI tools may use only data allowed for that tool.",
                }
            ],
            model="test-model",
        )

        self.assertIn("allowed data [1]", answer)
        self.assertEqual(calls[0][1], "GET")
        self.assertTrue(calls[0][0].endswith("/api/tags"))
        self.assertEqual(calls[1][1], "POST")
        self.assertTrue(calls[1][0].endswith("/api/chat"))
        self.assertEqual(calls[1][2]["model"], "test-model")
        self.assertFalse(calls[1][2]["stream"])
        prompt = calls[1][2]["messages"][1]["content"]
        self.assertIn("policy.md#chunk-0", prompt)
        self.assertIn("Approved AI tools", prompt)

    def test_missing_model_stops_before_chat_and_never_downloads(self):
        calls = []

        def fake_request(url, method, payload, timeout):
            calls.append((url, method))
            return {"models": []}

        client = OllamaClient(request_json=fake_request)

        with self.assertRaises(OllamaModelUnavailable):
            client.generate_grounded_answer(
                "question",
                [{"source_path": "source.md", "chunk_index": 0, "text": "evidence"}],
                model="not-installed",
            )

        self.assertEqual(calls, [("http://127.0.0.1:11434/api/tags", "GET")])

    def test_non_loopback_url_and_cloud_model_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_local_ollama_url("http://192.168.1.20:11434")
        with self.assertRaises(ValueError):
            validate_local_model_name("gpt-oss:120b-cloud")

    def test_short_model_name_does_not_match_cloud_variant(self):
        calls = []

        def fake_request(url, method, payload, timeout):
            calls.append((url, method))
            return {"models": [{"name": "gpt-oss:120b-cloud"}]}

        client = OllamaClient(request_json=fake_request)
        with self.assertRaises(OllamaModelUnavailable):
            client.generate_grounded_answer(
                "question",
                [{"source_path": "source.md", "chunk_index": 0, "text": "evidence"}],
                model="gpt-oss",
            )
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
