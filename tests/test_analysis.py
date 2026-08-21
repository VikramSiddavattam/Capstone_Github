from locator_lense.extractor import extract_elements, normalize_text
from locator_lense.parser import parse_html
from locator_lense.styles import resolve_styles
from locator_lense.technology import detect_technology


HTML = """
<html><head><title>  Demo  Page </title><style>.primary { color: red; }</style></head>
<body><h1>  Main   Heading </h1><h2 hidden>Hidden</h2>
<button class="primary" aria-label="Save"> Save </button>
<div role="button" tabindex="0">  Click\n me </div><a href="/next">Next</a>
</body></html>
"""


def test_extractor_finds_visible_elements_once_and_normalizes_text():
    elements = extract_elements(parse_html(HTML))

    assert [element.text for element in elements] == ["Main Heading", "Save", "Click me", "Next"]
    assert len(elements) == 4
    assert elements[2].category == "interactable"


def test_normalize_text_collapses_whitespace():
    assert normalize_text("  one\n\t two  ") == "one two"


def test_style_resolver_prefers_inline_over_embedded_css():
    soup = parse_html(HTML.replace('class="primary"', 'class="primary" style="color: blue; font-size: 12px"'))

    styles = resolve_styles(soup.select_one("button"), soup)

    assert styles["color"] == "blue"
    assert styles["font_size"] == "12px"


def test_style_resolver_honors_important_declarations():
    soup = parse_html('<style>button { color: red !important; }</style><button style="color: blue">Save</button>')

    styles = resolve_styles(soup.select_one("button"), soup)

    assert styles["color"] == "red"


def test_technology_detector_returns_not_detected_or_signature():
    assert detect_technology(parse_html("<html></html>")) == "Not detected"
    assert detect_technology(parse_html('<meta name="generator" content="DemoCMS">')) == "DemoCMS"
