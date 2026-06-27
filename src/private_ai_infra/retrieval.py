from __future__ import annotations

import json
from pathlib import Path
import re


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "do",
    "does",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


def search_index(index_path: Path, query: str, *, top_k: int = 3) -> list[dict[str, object]]:
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    query_terms = set(_tokenize(query))
    scored: list[dict[str, object]] = []

    for entry in payload.get("entries", []):
        terms = set(entry.get("terms", []))
        overlap = query_terms & terms
        phrase_bonus = 2 if query.lower() in str(entry.get("text", "")).lower() else 0
        score = len(overlap) + phrase_bonus
        if score <= 0:
            continue
        result = dict(entry)
        result["score"] = score
        result["matched_terms"] = sorted(overlap)
        scored.append(result)

    scored.sort(key=lambda item: (-int(item["score"]), str(item["source_path"]), int(item["chunk_index"])))
    return scored[:top_k]


def has_sufficient_evidence(query: str, matches: list[dict[str, object]]) -> bool:
    significant_terms = set(_tokenize(query)) - STOP_WORDS
    if not significant_terms or not matches:
        return False
    return any(significant_terms & set(match.get("matched_terms", [])) for match in matches)


def format_retrieval_answer(query: str, matches: list[dict[str, object]]) -> str:
    lines = [
        "Retrieval-only response",
        "",
        "No local model was requested or available. These are cited source excerpts from the local index.",
        "",
        f"Query: {query}",
        "",
    ]
    if not matches:
        lines.append("No matching indexed sources found.")
        return "\n".join(lines)

    for index, match in enumerate(matches, start=1):
        source = match["source_path"]
        chunk_index = match["chunk_index"]
        score = match["score"]
        excerpt = _excerpt(str(match["text"]))
        lines.append(f"[{index}] {source}#chunk-{chunk_index} score={score}")
        lines.append(excerpt)
        lines.append("")
    return "\n".join(lines).rstrip()


def format_grounded_answer(
    query: str,
    answer: str,
    matches: list[dict[str, object]],
    *,
    model: str,
) -> str:
    lines = [
        "Local model RAG response",
        "",
        f"Model: {model}",
        f"Query: {query}",
        "",
        "Answer:",
        answer.strip(),
        "",
        "Sources:",
    ]
    for index, match in enumerate(matches, start=1):
        source = match["source_path"]
        chunk_index = match["chunk_index"]
        score = match["score"]
        lines.append(f"[{index}] {source}#chunk-{chunk_index} score={score}")
    return "\n".join(lines)


def format_insufficient_evidence_refusal(query: str) -> str:
    return "\n".join(
        [
            "Local RAG refusal",
            "",
            f"Query: {query}",
            "",
            "I cannot answer this question from the approved indexed sources.",
            "Add an approved source containing the answer, then ingest it and try again.",
        ]
    )


def _excerpt(text: str, *, limit: int = 420) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())
