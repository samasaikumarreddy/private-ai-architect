import unittest

from private_ai_infra.models import default_answers, get_profile, normalize_mode


class ModelTests(unittest.TestCase):
    def test_mode_aliases(self):
        self.assertEqual(normalize_mode("local-dev"), "local-developer")
        self.assertEqual(normalize_mode("DGX Spark"), "dgx-enterprise")
        self.assertEqual(normalize_mode("hybrid"), "hybrid-gateway")

    def test_unknown_mode_fails(self):
        with self.assertRaises(ValueError):
            normalize_mode("unsafe-cloud")

    def test_default_answers_use_profile_defaults(self):
        answers = default_answers(
            mode="gpu-server",
            project_name="demo",
            company_name="acme",
        )
        profile = get_profile("gpu-server")
        self.assertEqual(answers.llm_runtime, profile.default_runtime)
        self.assertEqual(answers.vector_db, profile.default_vector_db)
        self.assertTrue(answers.audit_logging_required)


if __name__ == "__main__":
    unittest.main()

