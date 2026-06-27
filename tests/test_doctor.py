import unittest
from unittest.mock import patch

from private_ai_infra.doctor import run_doctor


class DoctorTests(unittest.TestCase):
    def test_local_ollama_api_is_detected_when_executable_is_not_on_path(self):
        with (
            patch("private_ai_infra.doctor.shutil.which", return_value=None),
            patch("private_ai_infra.doctor.OllamaClient") as client_type,
        ):
            client_type.return_value.list_installed_models.return_value = ("llama3.2:1b",)

            report = run_doctor()

        self.assertTrue(any("ollama: local API available" in check for check in report.checks))
        self.assertFalse(any("ollama:" in warning for warning in report.warnings))


if __name__ == "__main__":
    unittest.main()
