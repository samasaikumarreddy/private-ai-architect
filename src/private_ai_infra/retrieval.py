from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path
import re


BM25_K1 = 1.5
BM25_B = 0.75
RELATIVE_SCORE_FLOOR = 0.65
MIN_EVIDENCE_COVERAGE = 0.34
_CITATION_PATTERN = re.compile(r"\[(\d+)\]")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "could",
    "do",
    "does",
    "explain",
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
    "present",
    "please",
    "show",
    "should",
    "tell",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
    "would",
}


def search_index(index_path: Path, query: str, *, top_k: int = 3) -> list[dict[str, object]]:
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    entries = [entry for entry in payload.get("entries", []) if isinstance(entry, dict)]
    query_tokens = [term for term in _tokenize(query) if term not in STOP_WORDS]
    query_terms = set(query_tokens)
    if not query_terms:
        return []

    document_stats: list[tuple[dict[str, object], Counter[str], int]] = []
    document_frequency: Counter[str] = Counter()
    for entry in entries:
        frequencies = _entry_term_frequencies(entry)
        token_count = _entry_token_count(entry, frequencies)
        document_stats.append((entry, frequencies, token_count))
        document_frequency.update(query_terms & frequencies.keys())

    if not document_stats:
        return []
    average_length = sum(item[2] for item in document_stats) / len(document_stats)
    scored: list[dict[str, object]] = []

    for entry, frequencies, token_count in document_stats:
        overlap = query_terms & frequencies.keys()
        score = _bm25_score(
            query_tokens,
            frequencies,
            token_count=token_count,
            average_length=average_length,
            document_count=len(document_stats),
            document_frequency=document_frequency,
        )
        if query.strip().lower() in str(entry.get("text", "")).lower():
            score += 1.0
        source_terms = set(_tokenize(str(entry.get("source_name", ""))))
        score += 0.25 * len(query_terms & source_terms)
        if score <= 0:
            continue
        result = dict(entry)
        result["score"] = round(score, 4)
        result["matched_terms"] = sorted(overlap)
        scored.append(result)

    scored.sort(key=lambda item: (-float(item["score"]), str(item["source_path"]), int(item["chunk_index"])))
    if not scored:
        return []
    minimum_score = float(scored[0]["score"]) * RELATIVE_SCORE_FLOOR
    return [item for item in scored if float(item["score"]) >= minimum_score][:top_k]


def has_sufficient_evidence(query: str, matches: list[dict[str, object]]) -> bool:
    significant_terms = meaningful_terms(query)
    if not significant_terms or not matches:
        return False
    covered_terms: set[str] = set()
    for match in matches:
        covered_terms.update(significant_terms & set(match.get("matched_terms", [])))
    required_terms = max(1, math.ceil(len(significant_terms) * MIN_EVIDENCE_COVERAGE))
    return len(covered_terms) >= required_terms


def meaningful_terms(text: str) -> set[str]:
    return set(_tokenize(text)) - STOP_WORDS


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
        score = _format_score(match["score"])
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
    cited_numbers = sorted(
        {
            int(value)
            for value in _CITATION_PATTERN.findall(answer)
            if 1 <= int(value) <= len(matches)
        }
    )
    for index in cited_numbers:
        match = matches[index - 1]
        source = match["source_path"]
        chunk_index = match["chunk_index"]
        score = _format_score(match["score"])
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


def _entry_term_frequencies(entry: dict[str, object]) -> Counter[str]:
    stored = entry.get("term_frequencies")
    if isinstance(stored, dict):
        frequencies: Counter[str] = Counter()
        for term, count in stored.items():
            if isinstance(term, str) and isinstance(count, int) and count > 0:
                frequencies[term] = count
        if frequencies:
            return frequencies
    return Counter(_tokenize(str(entry.get("text", ""))))


def _entry_token_count(entry: dict[str, object], frequencies: Counter[str]) -> int:
    stored = entry.get("token_count")
    if isinstance(stored, int) and stored > 0:
        return stored
    return sum(frequencies.values())


def _bm25_score(
    query_tokens: list[str],
    frequencies: Counter[str],
    *,
    token_count: int,
    average_length: float,
    document_count: int,
    document_frequency: Counter[str],
) -> float:
    score = 0.0
    length_ratio = token_count / average_length if average_length else 1.0
    for term in set(query_tokens):
        frequency = frequencies.get(term, 0)
        if frequency <= 0:
            continue
        containing_documents = document_frequency[term]
        inverse_document_frequency = math.log(
            1 + (document_count - containing_documents + 0.5) / (containing_documents + 0.5)
        )
        denominator = frequency + BM25_K1 * (1 - BM25_B + BM25_B * length_ratio)
        score += inverse_document_frequency * (frequency * (BM25_K1 + 1) / denominator)
    return score


def _format_score(value: object) -> str:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{score:.3f}".rstrip("0").rstrip(".")
