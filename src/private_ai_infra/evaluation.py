from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .retrieval import has_sufficient_evidence, search_index


@dataclass(frozen=True)
class EvaluationCaseResult:
    case_id: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class EvaluationReport:
    results: tuple[EvaluationCaseResult, ...]

    @property
    def passed(self) -> int:
        return sum(result.passed for result in self.results)

    @property
    def ok(self) -> bool:
        return self.passed == len(self.results)

    def to_text(self) -> str:
        lines = [
            "Private AI retrieval evaluation",
            "",
            f"Passed: {self.passed}/{len(self.results)}",
            "",
            "Cases:",
        ]
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            lines.append(f"- {status} {result.case_id}: {result.detail}")
        return "\n".join(lines)


def evaluate_index(index_path: Path, cases_path: Path, *, top_k: int = 3) -> EvaluationReport:
    payload = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = payload.get("cases") if isinstance(payload, dict) else None
    if not isinstance(cases, list) or not cases:
        raise ValueError("Evaluation file must contain a non-empty 'cases' list.")

    results: list[EvaluationCaseResult] = []
    seen_ids: set[str] = set()
    for position, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Evaluation case {position} must be an object.")
        case_id = case.get("id")
        query = case.get("query")
        should_retrieve = case.get("should_retrieve", True)
        expected_sources = case.get("expected_sources", [])
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"Evaluation case {position} requires a non-empty string id.")
        if case_id in seen_ids:
            raise ValueError(f"Duplicate evaluation case id: {case_id}")
        seen_ids.add(case_id)
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"Evaluation case '{case_id}' requires a non-empty query.")
        if not isinstance(should_retrieve, bool):
            raise ValueError(f"Evaluation case '{case_id}' has a non-boolean should_retrieve value.")
        if not isinstance(expected_sources, list) or not all(
            isinstance(source, str) and source for source in expected_sources
        ):
            raise ValueError(f"Evaluation case '{case_id}' has invalid expected_sources.")

        matches = search_index(index_path, query, top_k=top_k)
        evidence_found = has_sufficient_evidence(query, matches)
        retrieved_names = {str(match.get("source_name", "")) for match in matches}
        retrieved_paths = {str(match.get("source_path", "")).replace("\\", "/") for match in matches}

        if should_retrieve:
            source_hit = not expected_sources or any(
                expected in retrieved_names or any(path.endswith(expected.replace("\\", "/")) for path in retrieved_paths)
                for expected in expected_sources
            )
            passed = evidence_found and source_hit
            detail = (
                f"retrieved {', '.join(sorted(retrieved_names)) or 'no sources'}"
                if passed
                else f"expected {', '.join(expected_sources) or 'supporting evidence'}; "
                f"retrieved {', '.join(sorted(retrieved_names)) or 'no sources'}"
            )
        else:
            passed = not evidence_found
            detail = "refused unsupported query" if passed else "unexpected supporting evidence"

        results.append(EvaluationCaseResult(case_id=case_id, passed=passed, detail=detail))

    return EvaluationReport(results=tuple(results))
