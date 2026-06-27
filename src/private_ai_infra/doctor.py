from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

from .ollama import OllamaClient, OllamaError


@dataclass(frozen=True)
class DoctorReport:
    checks: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_text(self) -> str:
        lines = ["Private AI doctor report", ""]
        lines.append("Checks:")
        lines.extend(f"- {check}" for check in self.checks)
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in self.warnings) if self.warnings else lines.append("- None")
        return "\n".join(lines)


def run_doctor() -> DoctorReport:
    checks: list[str] = []
    warnings: list[str] = []

    checks.append(f"Python: {sys.version.split()[0]}")
    if sys.version_info < (3, 11):
        warnings.append("Python 3.11 or newer is recommended.")

    checks.append(f"OS: {platform.system()} {platform.release()}")
    checks.append(f"Machine: {platform.machine()}")

    for command in ("git", "docker", "nvidia-smi"):
        path = shutil.which(command)
        if path:
            version = _command_version(command)
            checks.append(f"{command}: found at {path}{version}")
        else:
            warnings.append(f"{command}: not found")

    ollama_path = shutil.which("ollama")
    if ollama_path:
        checks.append(f"ollama: found at {ollama_path}{_command_version('ollama')}")
    else:
        try:
            installed_models = OllamaClient(timeout=1.0).list_installed_models()
            checks.append(
                "ollama: local API available at http://127.0.0.1:11434 "
                f"({len(installed_models)} installed model name(s))"
            )
        except OllamaError:
            warnings.append("ollama: executable not found and local API unavailable")

    if shutil.which("docker") is None:
        warnings.append("Docker is needed for the planned local RAG MVP stack.")
    if shutil.which("nvidia-smi") is None:
        warnings.append("No NVIDIA GPU tool detected. CPU/local mode may still be valid.")

    return DoctorReport(checks=tuple(checks), warnings=tuple(warnings))


def _command_version(command: str) -> str:
    args_by_command = {
        "git": ["git", "--version"],
        "docker": ["docker", "--version"],
        "ollama": ["ollama", "--version"],
        "nvidia-smi": ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
    }
    try:
        completed = subprocess.run(
            args_by_command[command],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    output = (completed.stdout or completed.stderr).strip().splitlines()
    if not output:
        return ""
    return f" ({output[0]})"
