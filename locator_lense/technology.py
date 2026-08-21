"""Deterministic best-effort technology signature detection."""

from bs4 import BeautifulSoup


SIGNATURES = (
    ("React", ("react", "reactdom")),
    ("Vue", ("vue", "__vue__")),
    ("Angular", ("ng-version", "angular")),
    ("Bootstrap", ("bootstrap",)),
    ("WordPress", ("wp-content", "wordpress")),
)


def detect_technology(soup: BeautifulSoup, linked_css: dict[str, str] | None = None) -> str:
    haystack = str(soup).lower() + " " + " ".join((linked_css or {}).values()).lower()
    generator = soup.find("meta", attrs={"name": lambda value: str(value).lower() == "generator"})
    if generator and generator.get("content"):
        return str(generator["content"])
    for technology, markers in SIGNATURES:
        if any(marker in haystack for marker in markers):
            return technology
    return "Not detected"
