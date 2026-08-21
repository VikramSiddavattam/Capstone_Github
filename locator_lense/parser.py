"""Canonical HTML parsing helpers."""

from bs4 import BeautifulSoup


def parse_html(html: str) -> BeautifulSoup:
    """Parse HTML tolerantly using the canonical lxml-backed DOM."""
    return BeautifulSoup(html or "", "lxml")


def extract_title(soup: BeautifulSoup) -> str:
    """Return the normalized document title or an empty string."""
    title = soup.find("title")
    return " ".join(title.get_text(" ", strip=True).split()) if title else ""
