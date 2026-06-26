import json
import tempfile
import unittest
from pathlib import Path

from private_ai_infra.generator import generate_dry_run
from private_ai_infra.models import default_answers
from private_ai_infra.validator import REQUIRED_DRY_RUN_FILES, validate_dry_run


class GeneratorValidatorTests(unittest.TestCase):
    def test_generate_dry_run_creates_required_files_and_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dry-run"
            answers = default_answers(
                mode="local-developer",
                project_name="demo",
                company_name="acme",
            )

            generated = generate_dry_run(output, answers)

            self.assertEqual(set(generated), set(REQUIRED_DRY_RUN_FILES))
            for filename in REQUIRED_DRY_RUN_FILES:
                self.assertTrue((output / filename).exists(), filename)

            result = validate_dry_run(output)
            self.assertTrue(result.ok, result.to_text())
            self.assertIn("proposed-env.example", result.checked_files)

            answers = json.loads((output / "answers.json").read_text(encoding="utf-8"))
            summary = json.loads((output / "dry-run-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(answers["mode"], "local-developer")
            self.assertFalse(summary["applied"])
            self.assertEqual(summary["mutations_performed"], [])

    def test_generate_dry_run_requires_force_for_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dry-run"
            answers = default_answers(
                mode="local-developer",
                project_name="demo",
                company_name="acme",
            )
            generate_dry_run(output, answers)

            with self.assertRaises(FileExistsError):
                generate_dry_run(output, answers)

            generate_dry_run(output, answers, force=True)

    def test_validation_fails_for_missing_required_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dry-run"
            output.mkdir()

            result = validate_dry_run(output)

            self.assertFalse(result.ok)
            self.assertIn("Missing required dry-run file: architecture-plan.md", result.errors)

    def test_validation_blocks_public_bind(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dry-run"
            answers = default_answers(
                mode="local-developer",
                project_name="demo",
                company_name="acme",
            )
            generate_dry_run(output, answers)
            env_path = output / "proposed-env.example"
            env_text = env_path.read_text(encoding="utf-8").replace(
                "PRIVATE_AI_BIND_HOST=127.0.0.1",
                "PRIVATE_AI_BIND_HOST=0.0.0.0",
            )
            env_path.write_text(env_text, encoding="utf-8")

            result = validate_dry_run(output)

            self.assertFalse(result.ok)
            self.assertTrue(any("bind host is public" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
