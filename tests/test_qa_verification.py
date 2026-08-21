from pathlib import Path

import pytest

from app import create_app
from locator_lense.extractor import extract_elements
from locator_lense.fetcher import Fetcher
from locator_lense.locators import generate_locator
from locator_lense.parser import parse_html

ROOT = Path(__file__).parents[1]


@pytest.fixture
def client():
    return create_app().test_client()


def test_qa_raw_html_happy_path_covers_required_report_fields(client):
    html = """
    <title>QA Page</title>
    <style>.primary { font-family: Arial; font-size: 16px; color: red; }</style>
    <h1>  Main   Heading </h1>
    <h2>Subheading</h2>
    <button id="save" class="primary" aria-label="Save"> Save </button>
    <a href="/next">Next</a>
    <input name="email" placeholder="Email">
    <select data-testid="country"><option>US</option></select>
    <textarea>Notes</textarea>
    <div role="button" tabindex="0">Click</div>
    """

    response = client.post("/analyze", data={"raw_html": html})
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    for expected in ("Locator Lense", "QA Page", "Main Heading", "Subheading", "font-family", "font-size", "color", "Locator", "Matches", "Score"):
        assert expected in body
    assert "#save" in body
    assert "Non-Unique" not in body


def test_qa_empty_and_multiple_inputs_are_rejected(client):
    for data in ({}, {"url": "https://example.com", "raw_html": "<button>Both</button>"}):
        response = client.post("/analyze", data=data)
        assert response.status_code == 400
        assert "exactly one" in response.get_data(as_text=True)


def test_qa_invalid_url_is_graceful(client):
    response = client.post("/analyze", data={"url": "ftp://example.com/page"})

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "http:// or https://" in body
    assert "Locator Lense" in body


def test_qa_missing_data_reports_fallbacks(client):
    response = client.post("/analyze", data={"raw_html": "<main>Empty report page</main>"})
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Not available" in body
    assert "Not detected" in body
    assert "No matching visible elements found." in body


def test_qa_hidden_and_invalid_tabindex_elements_are_excluded():
    soup = parse_html("""
        <button hidden>Hidden</button>
        <button aria-hidden="true">Hidden too</button>
        <button style="display: none">Hidden style</button>
        <input type="hidden" name="token" value="secret">
        <div tabindex="bad">Invalid tabindex</div>
        <button>Visible</button>
    """)

    elements = extract_elements(soup)

    assert [element.text for element in elements] == ["Visible"]


def test_qa_hidden_ancestor_excludes_visible_descendants():
    soup = parse_html('<section hidden><button>Hidden child</button></section><button>Visible</button>')

    elements = extract_elements(soup)

    assert [element.text for element in elements] == ["Visible"]


def test_qa_special_character_locator_is_unique_and_targeting():
    soup = parse_html('<button id="save:primary">Save</button>')
    tag = soup.find("button")

    result = generate_locator(tag, soup)

    assert result.locator_type == "id"
    assert result.match_count == 1
    assert len(soup.select(result.locator)) == 1


def test_qa_url_validation_matrix():
    assert Fetcher.validate_url("http://example.com") is None
    assert Fetcher.validate_url("https://example.com/path") is None
    for url in ("", "ftp://example.com", "https://", "example.com"):
        assert Fetcher.validate_url(url) is not None


def test_qa_requirements_document_has_all_required_sections_and_decisions():
    text = (ROOT / "documentation" / "requirements.md").read_text(encoding="utf-8")
    required_sections = (
        "## 1. Summary",
        "## 2. Functional Requirements",
        "## 3. Non-Functional Requirements",
        "## 4. Assumptions",
        "## 5. Edge Cases",
        "## 6. Out of Scope",
        "## 7. Open Questions",
    )
    for section in required_sections:
        assert section in text
    for decision in ("HTTP", "raw HTML", "JavaScript", "Not available", "Non-Unique", "id"):
        assert decision in text
    assert "100" in text


def test_qa_architecture_document_covers_approved_components_and_constraints():
    text = (ROOT / "documentation" / "architecture.md").read_text(encoding="utf-8")
    for term in (
        "Web Layer",
        "Fetcher",
        "HTML Parser",
        "Element Extractor",
        "Style Resolver",
        "Locator Generator",
        "Technology Stack Detector",
        "Report Renderer",
        "http",
        "https",
        "timeout",
        "deterministic",
        "HTML-escapes",
        "SSRF protection",
        "deferred",
    ):
        assert term.lower() in text.lower()


def test_qa_implementation_plan_has_dependency_order_blockers_and_validation():
    text = (ROOT / "documentation" / "impl-plan.md").read_text(encoding="utf-8")
    for section in (
        "## 2. Dependency-Ordered Tasks",
        "## 3. One-Day MVP Priorities",
        "## 4. Explicitly Blocked or Deferred Work",
        "## 5. Testing and Validation",
        "## 6. MVP Completion Gate",
    ):
        assert section in text
    assert "Blocked until complete" in text
    assert "XPath" in text
    assert "HTML encoding" in text


def test_qa_documents_are_nonempty_and_utf8_readable():
    for filename in ("requirements.md", "architecture.md", "impl-plan.md"):
        path = ROOT / "documentation" / filename
        assert path.exists()
        assert path.stat().st_size > 500
        assert path.read_text(encoding="utf-8").strip()
