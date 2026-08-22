"""Deterministic preferred locator generation."""

import re
from dataclasses import dataclass, field
from typing import Any

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


@dataclass
class LocatorContext:
    soup: BeautifulSoup
    xpath_document: Any
    match_counts: dict[tuple[str, str], int] = field(default_factory=dict)


def create_locator_context(soup: BeautifulSoup) -> LocatorContext:
    return LocatorContext(soup=soup, xpath_document=lxml_html.fromstring(str(soup)))


def _css_escape(value: str) -> str:
    return re.sub(r"([^a-zA-Z0-9_-])", lambda match: "\\" + match.group(1), value)


def _css_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _xpath_literal(value: str) -> str:
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"


def _is_stable_class(value: str) -> bool:
    return not re.search(r"(^|[-_])(css|sc|jsx|ng|ember|hash)[-_]?[a-z0-9]{4,}$", value.lower())


def _stable_attribute_xpath(tag_name: str, attribute: str, value: str) -> str:
    return f".//{tag_name}[@{attribute}={_xpath_literal(value)}]"


def _ancestor_xpath(tag: Tag, ancestor: Tag, ancestor_attribute: str) -> str:
    ancestor_value = str(ancestor.get(ancestor_attribute))
    tag_name = tag.name
    ancestor_name = ancestor.name
    return (
        f".//{tag_name}[ancestor::{ancestor_name}[@{ancestor_attribute}="
        f"{_xpath_literal(ancestor_value)}]]"
    )


def _relative_xpath_candidates(tag: Tag) -> list[str]:
    candidates: list[str] = []
    tag_name = tag.name
    for attribute in ("id", "name", "data-testid", "aria-label", "role", "title", "placeholder"):
        if tag.get(attribute):
            candidates.append(_stable_attribute_xpath(tag_name, attribute, str(tag[attribute])))

    text = " ".join(tag.get_text(" ", strip=True).split())
    if text:
        literal = _xpath_literal(text)
        candidates.append(f".//{tag_name}[normalize-space(.)={literal}]")
        if len(text) >= 12:
            candidates.append(f".//{tag_name}[contains(normalize-space(.), {literal})]")

    ancestor = tag.parent
    while isinstance(ancestor, Tag):
        for attribute in ("id", "data-testid", "name", "aria-label", "role"):
            if ancestor.get(attribute):
                candidates.append(_ancestor_xpath(tag, ancestor, attribute))
                break
        if any(ancestor.get(attribute) for attribute in ("id", "data-testid", "name", "aria-label", "role")):
            break
        ancestor = ancestor.parent

    parent = tag.parent
    if isinstance(parent, Tag):
        same_tag_siblings = [child for child in parent.find_all(tag.name, recursive=False)]
        if len(same_tag_siblings) > 1:
            position = next(index for index, sibling in enumerate(same_tag_siblings, 1) if sibling is tag)
            candidates.append(f".//{parent.name}/{tag_name}[{position}]")

    return list(dict.fromkeys(candidates))


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


def _match_count(context: LocatorContext, locator_type: str, locator: str) -> int:
    cache_key = (locator_type, locator)
    if cache_key in context.match_counts:
        return context.match_counts[cache_key]
    soup = context.soup
    if locator_type == "id":
        try:
            count = len(soup.select(locator))
        except Exception:
            count = 0
    elif locator_type in {"name", "data-testid"}:
        value = locator.split("=", 1)[1].rsplit("]", 1)[0].strip('"')
        count = len(soup.find_all(attrs={locator_type: value}))
    elif locator_type == "CSS Selector":
        try:
            count = len(soup.select(locator))
        except Exception:
            count = 0
    elif locator_type == "XPath":
        try:
            count = len(context.xpath_document.xpath(locator))
        except (ValueError, TypeError):
            count = 0
    else:
        count = 0
    context.match_counts[cache_key] = count
    return count


def _candidate_pairs(tag: Tag) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if tag.get("id"):
        pairs.append(("id", "#" + _css_escape(str(tag["id"]))))
    if tag.get("name"):
        pairs.append(("name", f"[name={_css_quote(str(tag['name']))}]"))
    if tag.get("data-testid"):
        pairs.append(("data-testid", f"[data-testid={_css_quote(str(tag['data-testid']))}]"))
    pairs.extend(("XPath", candidate) for candidate in _relative_xpath_candidates(tag))
    pairs.extend(("CSS Selector", candidate) for candidate in _css_candidates(tag))
    return pairs


def _candidate_pairs_for_type(tag: Tag, locator_type: str) -> list[tuple[str, str]]:
    if locator_type == "id" and tag.get("id"):
        return [("id", "#" + _css_escape(str(tag["id"])))]
    if locator_type == "name" and tag.get("name"):
        return [("name", f"[name={_css_quote(str(tag['name']))}]")]
    if locator_type == "data-testid" and tag.get("data-testid"):
        return [("data-testid", f"[data-testid={_css_quote(str(tag['data-testid']))}]")]
    if locator_type == "XPath":
        return [("XPath", candidate) for candidate in _relative_xpath_candidates(tag)]
    if locator_type == "CSS Selector":
        return [("CSS Selector", candidate) for candidate in _css_candidates(tag)]
    return []


def generate_locator(tag: Tag, soup: BeautifulSoup, context: LocatorContext | None = None) -> LocatorResult:
    active_context = context or create_locator_context(soup)
    non_unique_candidates: list[tuple[str, str, int, bool]] = []
    for locator_type in LOCATOR_PRIORITY:
        type_candidates: list[tuple[str, str, int, bool]] = []
        for _, locator in _candidate_pairs_for_type(tag, locator_type):
            match_count = _match_count(active_context, locator_type, locator)
            candidate = (locator_type, locator, match_count, match_count == 1)
            type_candidates.append(candidate)
            if match_count != 1:
                non_unique_candidates.append(candidate)
        unique_candidates = [candidate for candidate in type_candidates if candidate[3]]
        if unique_candidates:
            selected = unique_candidates[0]
            break
    else:
        selected = min(non_unique_candidates, key=lambda item: (LOCATOR_PRIORITY.index(item[0]), item[2], len(item[1]), item[1]))
    locator_type, locator, match_count, is_unique = selected
    return LocatorResult(
        locator=locator,
        locator_type=locator_type,
        match_count=match_count,
        score=LOCATOR_SCORES[locator_type],
        uniqueness="" if is_unique else "Non-Unique",
    )
