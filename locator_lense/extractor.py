"""Static DOM element extraction rules."""

import re
from collections.abc import Iterable

from bs4 import BeautifulSoup, Tag

from .models import ElementRecord

INTERACTABLE_TAGS = {"a", "button", "input", "select", "textarea"}
INTERACTABLE_ROLES = {"button", "link", "tab", "menuitem", "option"}
RELEVANT_ATTRIBUTES = (
    "id",
    "name",
    "class",
    "role",
    "href",
    "type",
    "value",
    "placeholder",
    "aria-label",
    "aria-labelledby",
    "data-testid",
    "tabindex",
)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _style_hides(tag: Tag) -> bool:
    style = normalize_text(str(tag.get("style", ""))).lower().replace(" ", "")
    return "display:none" in style or "visibility:hidden" in style


def is_visible(tag: Tag) -> bool:
    current: Tag | None = tag
    while current is not None:
        if current.has_attr("hidden") or str(current.get("aria-hidden", "")).lower() == "true":
            return False
        if _style_hides(current):
            return False
        parent = current.parent
        current = parent if isinstance(parent, Tag) else None
    return True


def _category(tag: Tag) -> str | None:
    tag_name = tag.name.lower()
    role = str(tag.get("role", "")).lower()
    categories: list[str] = []
    if tag_name == "h1":
        categories.append("heading")
    elif tag_name in {"h2", "h3", "h4", "h5", "h6"}:
        categories.append("subheading")
    if role == "heading":
        categories.append("heading" if tag_name == "h1" else "subheading")
    if tag_name in INTERACTABLE_TAGS or role in INTERACTABLE_ROLES:
        categories.append("interactable")
    tabindex = tag.get("tabindex")
    try:
        if tabindex is not None and int(str(tabindex).strip()) >= 0:
            categories.append("interactable")
    except ValueError:
        pass
    return ", ".join(dict.fromkeys(categories)) or None


def _attributes(tag: Tag) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for name in RELEVANT_ATTRIBUTES:
        if name in tag.attrs:
            value = tag.attrs[name]
            attributes[name] = " ".join(str(item) for item in value) if isinstance(value, list) else str(value)
    return attributes


def extract_element_tags(soup: BeautifulSoup) -> list[Tag]:
    return [tag for tag in soup.find_all(True) if _category(tag) is not None and is_visible(tag)]


def extract_elements(soup: BeautifulSoup) -> list[ElementRecord]:
    records: list[ElementRecord] = []
    for tag in extract_element_tags(soup):
        category = _category(tag)
        assert category is not None
        records.append(
            ElementRecord(
                category=category,
                text=normalize_text(tag.get_text(" ", strip=False)),
                tag_name=tag.name,
                attributes=_attributes(tag),
            )
        )
    return records
