import tempfile
import unittest
from pathlib import Path

from private_ai_infra.cli import main


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


if __name__ == "__main__":
    unittest.main()
