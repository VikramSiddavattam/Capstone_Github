"""Shared immutable result contracts for the analysis pipeline."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FetchResult:
    html: str | None
    final_url: str | None
    error: str | None = None


@dataclass(frozen=True)
class ElementRecord:
    category: str
    text: str
    tag_name: str
    attributes: dict[str, str]
    locator: str = "Not available"
    locator_type: str = "Not available"
    match_count: int = 0
    score: int = 0
    uniqueness: str = ""
    styles: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AnalysisResult:
    title: str
    final_url: str | None
    technology: str
    elements: list[ElementRecord]
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
