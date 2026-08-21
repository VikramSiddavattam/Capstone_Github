"""Conservative static CSS style resolution."""

from dataclasses import dataclass

import tinycss2
from bs4 import BeautifulSoup, Tag

from .extractor import normalize_text

STYLE_PROPERTIES = {
    "font-family": "font_family",
    "font-size": "font_size",
    "color": "color",
}


@dataclass(frozen=True)
class StyleRule:
    selector: str
    declarations: dict[str, str]
    order: int


def _declarations(css: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for token in tinycss2.parse_declaration_list(css, skip_whitespace=True, skip_comments=True):
        if token.type != "declaration" or token.name not in STYLE_PROPERTIES or token.important:
            continue
        value = normalize_text(tinycss2.serialize(token.value))
        if value:
            result[token.name] = value
    return result


def parse_rules(css: str) -> list[StyleRule]:
    rules: list[StyleRule] = []
    for order, token in enumerate(tinycss2.parse_stylesheet(css or "", skip_whitespace=True, skip_comments=True)):
        if token.type != "qualified-rule":
            continue
        selector = normalize_text(tinycss2.serialize(token.prelude))
        declarations = _declarations(tinycss2.serialize(token.content))
        if selector and declarations:
            rules.append(StyleRule(selector, declarations, order))
    return rules


def _specificity(selector: str) -> tuple[int, int, int]:
    return (selector.count("#"), selector.count(".") + selector.count("["), sum(1 for part in selector.replace(">", " ").split() if part and not part.startswith(("#", ".", "["))))


def resolve_styles(tag: Tag, soup: BeautifulSoup, linked_css: dict[str, str] | None = None) -> dict[str, str]:
    rules: list[StyleRule] = []
    for style in soup.find_all("style"):
        rules.extend(parse_rules(style.get_text()))
    for css in (linked_css or {}).values():
        rules.extend(parse_rules(css))
    selected: dict[str, tuple[tuple[int, int, int], int, str]] = {}
    for rule in rules:
        try:
            matches = soup.select(rule.selector)
        except Exception:
            continue
        if tag not in matches:
            continue
        rank = (_specificity(rule.selector), rule.order)
        for property_name, value in rule.declarations.items():
            current = selected.get(property_name)
            if current is None or rank >= (current[0], current[1]):
                selected[property_name] = (rank[0], rank[1], value)
    inline = _declarations(str(tag.get("style", "")))
    for property_name, value in inline.items():
        selected[property_name] = ((10_000, 0, 0), 10_000, value)
    return {STYLE_PROPERTIES[name]: selected[name][2] for name in STYLE_PROPERTIES if name in selected}
