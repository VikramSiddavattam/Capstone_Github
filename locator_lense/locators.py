"""Deterministic preferred locator generation."""

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag
from lxml import html as lxml_html

from .config import LOCATOR_PRIORITY, LOCATOR_SCORES


@dataclass(frozen=True)
class LocatorResult:
    locator: str
    locator_type: str
    match_count: int
    score: int
    uniqueness: str


def _css_escape(value: str) -> str:
    return re.sub(r"([^a-zA-Z0-9_-])", lambda match: "\\" + match.group(1), value)


def _css_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _is_stable_class(value: str) -> bool:
    return not re.search(r"(^|[-_])(css|sc|jsx|ng|ember|hash)[-_]?[a-z0-9]{4,}$", value.lower())


def _element_xpath(tag: Tag) -> str:
    parts: list[str] = []
    current: Tag | None = tag
    while current is not None and current.name not in {"[document]", "html"}:
        position = 1
        sibling = current.previous_sibling
        while sibling is not None:
            if isinstance(sibling, Tag) and sibling.name == current.name:
                position += 1
            sibling = sibling.previous_sibling
        parts.append(f"{current.name}[{position}]")
        parent = current.parent
        current = parent if isinstance(parent, Tag) else None
    return "/html[1]/" + "/".join(reversed(parts)) if parts else "//*"


def _css_candidates(tag: Tag) -> list[str]:
    candidates: list[str] = []
    tag_name = tag.name
    stable_classes = [str(value) for value in tag.get("class", []) if _is_stable_class(str(value))]
    if stable_classes:
        candidates.append(tag_name + "".join("." + _css_escape(value) for value in stable_classes))
    for attribute in ("role", "type", "aria-label", "placeholder"):
        if tag.has_attr(attribute):
            candidates.append(f"{tag_name}[{attribute}={_css_quote(str(tag[attribute]))}]")
    candidates.append(_element_css_path(tag))
    return list(dict.fromkeys(candidates))


def _element_css_path(tag: Tag) -> str:
    parts: list[str] = []
    current: Tag | None = tag
    while current is not None and current.name not in {"[document]", "html"}:
        part = current.name
        siblings = [sibling for sibling in current.parent.find_all(current.name, recursive=False)] if isinstance(current.parent, Tag) else []
        if len(siblings) > 1:
            position = next(index for index, sibling in enumerate(siblings, 1) if sibling is current)
            part += f":nth-of-type({position})"
        parts.append(part)
        parent = current.parent
        current = parent if isinstance(parent, Tag) else None
    return "html > " + " > ".join(reversed(parts))


def _match_count(soup: BeautifulSoup, locator_type: str, locator: str) -> int:
    if locator_type == "id":
        try:
            return len(soup.select(locator))
        except Exception:
            return 0
    if locator_type in {"name", "data-testid"}:
        value = locator.split("=", 1)[1].rsplit("]", 1)[0].strip('"')
        return len(soup.find_all(attrs={locator_type: value}))
    if locator_type == "CSS Selector":
        try:
            return len(soup.select(locator))
        except Exception:
            return 0
    if locator_type == "XPath":
        try:
            document = lxml_html.fromstring(str(soup))
            return len(document.xpath(locator))
        except (ValueError, TypeError):
            return 0
    return 0


def _candidate_pairs(tag: Tag) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if tag.get("id"):
        pairs.append(("id", "#" + _css_escape(str(tag["id"]))))
    if tag.get("name"):
        pairs.append(("name", f"[name={_css_quote(str(tag['name']))}]"))
    if tag.get("data-testid"):
        pairs.append(("data-testid", f"[data-testid={_css_quote(str(tag['data-testid']))}]"))
    pairs.extend(("CSS Selector", candidate) for candidate in _css_candidates(tag))
    pairs.append(("XPath", _element_xpath(tag)))
    return pairs


def generate_locator(tag: Tag, soup: BeautifulSoup) -> LocatorResult:
    candidates: list[tuple[str, str, int, bool]] = []
    for locator_type, locator in _candidate_pairs(tag):
        match_count = _match_count(soup, locator_type, locator)
        is_unique = match_count == 1
        candidates.append((locator_type, locator, match_count, is_unique))
    unique = [candidate for candidate in candidates if candidate[3]]
    if unique:
        selected = min(unique, key=lambda item: (LOCATOR_PRIORITY.index(item[0]), len(item[1]), item[1]))
    else:
        selected = min(candidates, key=lambda item: (LOCATOR_PRIORITY.index(item[0]), item[2], len(item[1]), item[1]))
    locator_type, locator, match_count, is_unique = selected
    return LocatorResult(
        locator=locator,
        locator_type=locator_type,
        match_count=match_count,
        score=LOCATOR_SCORES[locator_type],
        uniqueness="" if is_unique else "Non-Unique",
    )
