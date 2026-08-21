"""Flask entry point and request-to-report orchestration."""

from flask import Flask, render_template, request

from locator_lense.extractor import extract_element_tags, extract_elements
from locator_lense.fetcher import Fetcher
from locator_lense.locators import generate_locator
from locator_lense.models import AnalysisResult, ElementRecord
from locator_lense.parser import extract_title, parse_html
from locator_lense.styles import resolve_styles
from locator_lense.technology import detect_technology


def analyze_html(html: str, final_url: str | None = None, fetcher: Fetcher | None = None) -> AnalysisResult:
    soup = parse_html(html)
    linked_css = fetcher.fetch_linked_stylesheets(html, final_url) if fetcher and final_url else {}
    elements: list[ElementRecord] = []
    tags = extract_element_tags(soup)
    for tag, record in zip(tags, extract_elements(soup)):
        locator = generate_locator(tag, soup)
        styles = resolve_styles(tag, soup, linked_css)
        elements.append(
            ElementRecord(
                category=record.category,
                text=record.text,
                tag_name=record.tag_name,
                attributes=record.attributes,
                locator=locator.locator,
                locator_type=locator.locator_type,
                match_count=locator.match_count,
                score=locator.score,
                uniqueness=locator.uniqueness,
                styles=styles,
            )
        )
    return AnalysisResult(
        title=extract_title(soup) or "Not available",
        final_url=final_url,
        technology=detect_technology(soup, linked_css),
        elements=elements,
    )


def create_app(fetcher: Fetcher | None = None) -> Flask:
    app = Flask(__name__)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    active_fetcher = fetcher or Fetcher()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/analyze")
    def analyze():
        url = request.form.get("url", "").strip()
        raw_html = request.form.get("raw_html", "")
        supplied = bool(url) + bool(raw_html.strip())
        if supplied != 1:
            return render_template("report.html", result=AnalysisResult("Not available", None, "Not detected", [], "Provide exactly one URL or raw HTML input.")), 400

        if url:
            fetched = active_fetcher.fetch_html(url)
            if fetched.error:
                result = AnalysisResult("Not available", fetched.final_url, "Not detected", [], fetched.error)
            else:
                result = analyze_html(fetched.html or "", fetched.final_url, active_fetcher)
        else:
            result = analyze_html(raw_html)
        return render_template("report.html", result=result)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)