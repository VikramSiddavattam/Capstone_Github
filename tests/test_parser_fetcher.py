from unittest.mock import Mock

import requests

from locator_lense.fetcher import Fetcher
from locator_lense.parser import extract_title, parse_html


def test_parse_html_tolerates_malformed_markup_and_extracts_title():
    soup = parse_html("<title> Demo </title><div><p>text")

    assert extract_title(soup) == "Demo"
    assert soup.find("p").get_text() == "text"


def test_fetcher_rejects_non_http_url():
    result = Fetcher().fetch_html("file:///tmp/page.html")

    assert result.html is None
    assert "http:// or https://" in result.error


def test_fetcher_captures_final_url_and_html():
    session = Mock(spec=requests.Session)
    response = Mock()
    response.url = "https://final.example/page"
    response.text = "<html><title>Page</title></html>"
    response.headers = {"Content-Type": "text/html"}
    session.get.return_value = response
    fetcher = Fetcher(session=session)

    result = fetcher.fetch_html("https://start.example")

    response.raise_for_status.assert_called_once_with()
    assert result.final_url == "https://final.example/page"
    assert result.html == "<html><title>Page</title></html>"
    session.max_redirects = 10


def test_fetcher_handles_timeout():
    session = Mock(spec=requests.Session)
    session.get.side_effect = requests.Timeout()

    result = Fetcher(session=session).fetch_html("https://example.com")

    assert result.html is None
    assert result.error == "The URL request timed out."


def test_fetcher_handles_redirect_limit():
    session = Mock(spec=requests.Session)
    session.get.side_effect = requests.TooManyRedirects(request=Mock())

    result = Fetcher(session=session).fetch_html("https://example.com")

    assert result.error == "The URL exceeded the redirect limit."


def test_fetcher_fetches_direct_linked_css():
    session = Mock(spec=requests.Session)
    response = Mock()
    response.headers = {"Content-Type": "text/css"}
    response.text = ".primary { color: red; }"
    session.get.return_value = response

    stylesheets = Fetcher(session=session).fetch_linked_stylesheets(
        '<link rel="stylesheet" href="/styles.css">',
        "https://example.com/page",
    )

    assert stylesheets == {"https://example.com/styles.css": ".primary { color: red; }"}
