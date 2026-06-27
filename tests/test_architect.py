from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from private_ai_infra.architect import ARCHITECT_OUTPUT_FILES, generate_architect_pack
from private_ai_infra.blueprint import (
    BLUEPRINT_SCHEMA_VERSION,
    REQUIRED_TOP_LEVEL_KEYS,
    architect_answers_from_mapping,
    build_blueprint,
    calculate_blueprint_checksum,
    normalize_journey,
    validate_blueprint,
)
from private_ai_infra.cli import main


def complete_answers(journey: str = "local-rag") -> dict[str, object]:
    answers: dict[str, object] = {
        "journey": journey,
        "project_name": "demo",
        "owner_name": "example owner",
        "data_location": "on premises",
        "allowed_document_sources": ["./approved-docs"],
        "user_count": 10,
        "model_preference": "approved-model",
        "runtime_preference": "approved-runtime",
        "hardware_availability": "reviewed workstation",
        "network_exposure": "localhost" if journey == "local-rag" else "private-network",
        "compliance_concerns": ["none"],
        "authentication_rbac_needs": "named local users",
        "audit_logging_needs": "record access and validation",
        "data_owner_approval": "approved",
    }
    if journey == "private-gpu":
        answers.update(
            {
                "target_hardware": "DGX Spark planning input",
                "deployment_stage": "pilot",
            }
        )
    elif journey == "cloud-migration":
        answers.update(
            {
                "source_provider": "example provider",
                "source_workload": "approved workload description",
                "rollback_requirement": "document rollback before implementation",
            }
        )
    return answers


class GuidedArchitectTests(unittest.TestCase):
    def test_local_rag_interactive_flow_hides_cloud_questions(self):
        prompts: list[str] = []

        def answer_with_default(prompt: str) -> str:
            prompts.append(prompt)
            return ""

        with tempfile.TemporaryDirectory() as tmp:
            output = StringIO()
            with patch("builtins.input", side_effect=answer_with_default), redirect_stdout(output):
                code = main(
                    [
                        "architect",
                        "--journey",
                        "local-rag",
                        "--project-name",
                        "demo",
                        "--owner-name",
                        "local",
                        "--output-dir",
                        str(Path(tmp) / "architect"),
                    ]
                )

        prompt_text = "\n".join(prompts).lower()
        self.assertEqual(code, 0)
        self.assertIn("journey", prompts[0].lower())
        self.assertNotIn("source cloud provider", prompt_text)
        self.assertNotIn("source ai workload", prompt_text)
        self.assertNotIn("rollback requirement", prompt_text)

    def test_private_gpu_blueprint_is_planning_only(self):
        answers = architect_answers_from_mapping(complete_answers("private-gpu"))
        blueprint = build_blueprint(answers)
        result = validate_blueprint(blueprint)

        self.assertTrue(result.ok, result.to_text())
        self.assertTrue(blueprint["safety"]["planning_only"])
        self.assertFalse(blueprint["safety"]["infrastructure_changes"])
        self.assertEqual(
            set(blueprint["journey_details"]),
            {"target_hardware", "deployment_stage"},
        )
        self.assertTrue(any("DGX" in warning for warning in result.warnings))

    def test_cloud_migration_does_not_call_cloud_or_system_apis(self):
        with tempfile.TemporaryDirectory() as tmp:
            answers_file = Path(tmp) / "answers.json"
            answers_file.write_text(json.dumps(complete_answers("cloud-migration")), encoding="utf-8")
            with (
                patch("urllib.request.urlopen") as urlopen,
                patch("subprocess.run") as subprocess_run,
                redirect_stdout(StringIO()),
            ):
                code = main(
                    [
                        "architect",
                        "--answers-file",
                        str(answers_file),
                        "--output-dir",
                        str(Path(tmp) / "architect"),
                    ]
                )

            self.assertEqual(code, 0)
            urlopen.assert_not_called()
            subprocess_run.assert_not_called()
            blueprint = json.loads(
                (Path(tmp) / "architect" / "blueprint.json").read_text(encoding="utf-8")
            )
            self.assertFalse(blueprint["safety"]["discovery_performed"])
            self.assertEqual(
                set(blueprint["journey_details"]),
                {"source_provider", "source_workload", "rollback_requirement"},
            )

    def test_blueprint_schema_and_checksum_are_stable(self):
        answers = architect_answers_from_mapping(complete_answers())
        first = build_blueprint(answers)
        second = build_blueprint(answers)

        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], BLUEPRINT_SCHEMA_VERSION)
        self.assertEqual(set(first), set(REQUIRED_TOP_LEVEL_KEYS))
        self.assertEqual(first["blueprint_checksum"], calculate_blueprint_checksum(first))

    def test_blueprint_validation_rejects_missing_fields_and_tampering(self):
        blueprint = build_blueprint(
            architect_answers_from_mapping(complete_answers())
        )
        del blueprint["requirements"]["model_preference"]
        result = validate_blueprint(blueprint)

        self.assertFalse(result.ok)
        self.assertIn(
            "Missing required requirements field: model_preference",
            result.errors,
        )
        self.assertIn(
            "blueprint_checksum does not match the normalized blueprint content",
            result.errors,
        )

    def test_unknown_decisions_are_captured(self):
        answers = architect_answers_from_mapping(
            {
                "journey": "cloud-migration",
                "project_name": "unknowns",
            }
        )
        blueprint = build_blueprint(answers)
        decisions = "\n".join(blueprint["unresolved_decisions"])

        self.assertIn("Select or evaluate a model", decisions)
        self.assertIn("Select or evaluate a model runtime", decisions)
        self.assertIn("Identify the source cloud provider", decisions)
        self.assertIn("Define rollback requirements", decisions)
        self.assertIn("Confirm applicable compliance requirements", decisions)

    def test_public_exposure_and_missing_approval_generate_risks(self):
        values = complete_answers()
        values["network_exposure"] = "public"
        values["data_owner_approval"] = "pending"
        blueprint = build_blueprint(architect_answers_from_mapping(values))
        result = validate_blueprint(blueprint)
        risks = "\n".join(blueprint["known_risks"])
        warnings = "\n".join(result.warnings)

        self.assertIn("Public exposure", risks)
        self.assertIn("lack recorded data owner approval", risks)
        self.assertIn("Public network exposure", warnings)
        self.assertIn("Data owner approval is missing", warnings)

    def test_review_documents_are_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "architect"
            second_output_dir = Path(tmp) / "architect-copy"
            answers = architect_answers_from_mapping(complete_answers())
            result = generate_architect_pack(output_dir, answers)
            generate_architect_pack(second_output_dir, answers)

            self.assertEqual(set(result.generated_files), set(ARCHITECT_OUTPUT_FILES))
            for filename in ARCHITECT_OUTPUT_FILES:
                self.assertTrue((output_dir / filename).exists(), filename)
                self.assertEqual(
                    (output_dir / filename).read_text(encoding="utf-8"),
                    (second_output_dir / filename).read_text(encoding="utf-8"),
                    filename,
                )
            summary = (output_dir / "summary.md").read_text(encoding="utf-8")
            self.assertIn("Planning only", summary)
            self.assertIn("Infrastructure changes: none", summary)

    def test_invalid_journey_fails_safely(self):
        with self.assertRaises(ValueError):
            normalize_journey("deploy-production")

        blueprint = build_blueprint(
            architect_answers_from_mapping(complete_answers())
        )
        blueprint["journey"] = "deploy-production"
        blueprint["blueprint_checksum"] = calculate_blueprint_checksum(blueprint)
        result = validate_blueprint(blueprint)

        self.assertFalse(result.ok)
        self.assertTrue(any("journey must be one of" in error for error in result.errors))

    def test_secret_bearing_answer_fields_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "secret-bearing"):
            architect_answers_from_mapping(
                {
                    "journey": "local-rag",
                    "api_token": "must-not-be-accepted",
                }
            )

    def test_irrelevant_journey_fields_are_rejected_even_when_unknown(self):
        with self.assertRaisesRegex(ValueError, "only valid for cloud-migration"):
            architect_answers_from_mapping(
                {
                    "journey": "local-rag",
                    "source_provider": "unknown",
                }
            )


if __name__ == "__main__":
    unittest.main()
