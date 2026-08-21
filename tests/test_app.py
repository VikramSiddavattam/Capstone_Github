from app import create_app
from locator_lense.models import FetchResult


class StubFetcher:
    def __init__(self, result):
        self.result = result

    def fetch_html(self, url):
        return self.result

    def fetch_linked_stylesheets(self, html, base_url):
        return {"https://example.com/site.css": "button { color: red; }"}


def test_raw_html_generates_report():
    client = create_app().test_client()

    response = client.post("/analyze", data={"raw_html": '<title>Demo</title><button id="save">Save</button>'})

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Locator Lense" in body
    assert "Demo" in body
    assert "#save" in body


def test_both_inputs_are_rejected():
    client = create_app().test_client()

    response = client.post("/analyze", data={"url": "https://example.com", "raw_html": "<button>Save</button>"})

    assert response.status_code == 400
    assert "exactly one" in response.get_data(as_text=True)


def test_report_escapes_untrusted_html():
    client = create_app().test_client()

    response = client.post("/analyze", data={"raw_html": '<title>&lt;script&gt;alert(1)&lt;/script&gt;</title><button>Save</button>'})

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;" in body


def test_url_report_includes_final_url_and_linked_css():
    fetcher = StubFetcher(FetchResult('<title>Fetched</title><link rel="stylesheet" href="/site.css"><button>Go</button>', "https://example.com/final"))
    client = create_app(fetcher=fetcher).test_client()

    response = client.post("/analyze", data={"url": "https://example.com/start"})

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "https://example.com/final" in body
    assert "red" in body


def test_url_failure_renders_graceful_error():
    fetcher = StubFetcher(FetchResult(None, None, "The URL request timed out."))
    client = create_app(fetcher=fetcher).test_client()

    response = client.post("/analyze", data={"url": "https://example.com"})

    assert response.status_code == 200
    assert "The URL request timed out." in response.get_data(as_text=True)


def test_missing_page_fields_render_fallback_values():
    client = create_app().test_client()

    response = client.post("/analyze", data={"raw_html": "<main>Nothing to analyze</main>"})

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Not available" in body
    assert "Not detected" in body
    assert "No matching visible elements found." in body