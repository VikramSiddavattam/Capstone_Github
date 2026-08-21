"""HTTP retrieval for local/demo MVP analysis."""

from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .config import Settings
from .models import FetchResult


class Fetcher:
    """Fetch HTML and directly linked stylesheets with bounded requests."""

    def __init__(self, settings: Settings | None = None, session: requests.Session | None = None):
        self.settings = settings or Settings()
        self.session = session or requests.Session()
        self.session.max_redirects = self.settings.redirect_limit

    @staticmethod
    def validate_url(url: str) -> str | None:
        """Return an error message for invalid URL input, otherwise None."""
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return "URL must use http:// or https:// and include a host."
        return None

    def fetch_html(self, url: str) -> FetchResult:
        """Fetch a final HTML response and preserve its resolved URL."""
        validation_error = self.validate_url(url)
        if validation_error:
            return FetchResult(None, None, validation_error)

        try:
            response = self.session.get(
                url.strip(),
                allow_redirects=True,
                timeout=self.settings.request_timeout,
                headers={"Accept": "text/html,application/xhtml+xml"},
            )
            response.raise_for_status()
        except requests.TooManyRedirects:
            return FetchResult(None, None, "The URL exceeded the redirect limit.")
        except requests.Timeout:
            return FetchResult(None, None, "The URL request timed out.")
        except requests.RequestException as exc:
            return FetchResult(None, None, f"The URL could not be reached: {exc}")

        content_type = response.headers.get("Content-Type", "").lower()
        if content_type and "html" not in content_type and "text/plain" not in content_type:
            return FetchResult(None, str(response.url), "The final response is not HTML.")
        return FetchResult(response.text, str(response.url), None)

    def fetch_linked_stylesheets(self, html: str, base_url: str) -> dict[str, str]:
        """Fetch directly linked stylesheets; failed resources are skipped."""
        soup = BeautifulSoup(html or "", "lxml")
        stylesheets: dict[str, str] = {}
        for link in soup.find_all("link", href=True):
            rel = {str(value).lower() for value in link.get("rel", [])}
            if "stylesheet" not in rel:
                continue
            stylesheet_url = urljoin(base_url, str(link["href"]))
            if self.validate_url(stylesheet_url):
                continue
            try:
                response = self.session.get(
                    stylesheet_url,
                    allow_redirects=True,
                    timeout=self.settings.request_timeout,
                    headers={"Accept": "text/css,text/plain"},
                )
                response.raise_for_status()
                if "css" in response.headers.get("Content-Type", "").lower() or not response.headers.get("Content-Type"):
                    stylesheets[stylesheet_url] = response.text
            except requests.RequestException:
                continue
        return stylesheets
