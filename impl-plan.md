# Locator Lense MVP Implementation Plan

## 1. Plan Scope

Implement the approved local/demo MVP as a stateless Flask application that accepts exactly one input source, analyzes static server-delivered HTML, and returns an HTML report.

Production hardening remains deferred: SSRF protection, advanced resource controls, rate limiting, authentication, background jobs, browser rendering, and JavaScript execution.

## 2. Dependency-Ordered Tasks

### Phase 1: Project Foundation

1. Create the Python project structure:
   - `app.py` or Flask application package.
   - `locator_lense/` modules for fetching, parsing, extraction, styles, locators, technology detection, and reporting.
   - `templates/` for Jinja2 templates.
   - `tests/` for unit and integration tests.
2. Add `.gitignore` for virtual environments, Python caches, test output, and local configuration.
3. Choose and pin one CSS parser dependency. The architecture currently lists `tinycss2 / cssutils`; select one before implementing the Style Resolver.
4. Add pinned runtime dependencies for Flask, requests, BeautifulSoup, lxml, the selected CSS parser, and Jinja2, plus pytest for tests.
5. Define shared constants and result models for:
   - Redirect limit.
   - Connect and read timeouts.
   - Locator types and fixed scores.
   - `Not available`, `Not detected`, and `Non-Unique` report values.
6. Define component interfaces so the Fetcher, parser, analyzers, locator generator, and renderer can be tested independently.

**Blocked until complete:** All implementation work depends on the project structure, dependency choice, and shared result contracts.

### Phase 2: Input Route and Validation

7. Create the Flask route that serves the input form and accepts a POST submission.
8. Validate that exactly one of URL or raw HTML is provided.
9. Reject empty input, both inputs, invalid URL syntax, and unsupported schemes with a usable error result.
10. Configure Jinja2 autoescaping for the report templates from the start.

**Blocked until complete:** End-to-end request handling and report integration depend on the route validation contract.

### Phase 3: HTML Parser and URL Fetcher

11. Implement the HTML parser using BeautifulSoup with lxml.
12. Ensure malformed HTML produces a usable parse tree rather than an unhandled exception.
13. Implement URL validation for `http` and `https` only.
14. Implement the Fetcher with:
   - Automatic standard redirect following.
   - A fixed maximum redirect count.
   - Explicit connect and read timeouts.
   - Final resolved URL capture.
   - Clear unavailable/error results for network failures and final HTTP errors.
15. Parse raw HTML directly without a network request.
16. Resolve linked stylesheet URLs relative to the final page URL and fetch directly linked CSS resources using the configured timeout behavior.
17. Make linked-CSS failures degrade gracefully to missing style values.

**Blocked until complete:** Element extraction, style resolution, technology detection, and integration require a shared DOM. Style resolution also requires linked-resource results for URL inputs.

### Phase 4: Independent Analysis Passes

After the parser and input/resource contracts are available, these tasks can proceed in parallel.

#### 4A. Element Extractor

18. Extract headings: `h1` through `h6` and elements with ARIA heading roles.
19. Extract interactables: links, buttons, inputs, selects, textareas, roles `button`, `link`, `tab`, `menuitem`, and `option`, and elements with `tabindex >= 0`.
20. Deduplicate elements that match multiple extraction rules.
21. Implement static visibility checks for `hidden`, `aria-hidden="true"`, `display:none`, and `visibility:hidden` cues.
22. Normalize visible text by trimming leading/trailing whitespace and collapsing consecutive whitespace.
23. Preserve empty normalized text when an extracted visible element has no text.

#### 4B. Style Resolver

24. Parse inline styles, `<style>` blocks, and directly retrieved linked CSS using the selected CSS parser.
25. Resolve only font family, font size, and text color when static analysis is reliable.
26. Define deterministic precedence for supported declarations and return `Not available` for unsupported, conflicting, inherited, or uncertain values.

#### 4C. Technology Stack Detector

27. Detect technologies from available HTML, metadata, script/link patterns, and directly retrieved page resources.
28. Keep detection deterministic and best-effort.
29. Return `Not detected` when no reliable signal matches.

**Blocked until complete:** Locator generation is blocked until the Element Extractor returns elements and the complete DOM is available. Report rendering is blocked until all analysis result shapes are defined.

### Phase 5: Locator Generation

30. Build candidates in the fixed order: `id`, `name`, `data-testid`, XPath, CSS Selector.
31. Generate attribute-based candidates with correct escaping.
32. Generate deterministic CSS candidates that:
   - Prefer stable attributes.
   - Avoid volatile or autogenerated classes where possible.
   - Prefer the shortest candidate that uniquely identifies the target.
   - Use structural selectors as fallback.
33. Generate CSS selectors only after XPath candidates have been evaluated.
34. Calculate each candidate's match count against the complete analyzed DOM.
35. Apply fixed base scores:
   - `id`: 100
   - `name`: 90
   - `data-testid`: 85
   - CSS Selector: 75
   - XPath: 65
36. Prefer any unique locator over every non-unique locator.
37. If no candidate is unique, choose the highest-priority locator type and then the candidate with the lowest match count within that type.
38. Mark non-unique selections as `Non-Unique` while retaining their base score.
39. Apply deterministic tie-breaking for candidates with equal priority and match count.
40. Report only the selected locator, locator type, match count, and score.

**Blocked until complete:** The Report Renderer needs the final locator result model. Locator matching cannot be finalized until the parser's DOM representation and selector evaluation approach are fixed.

### Phase 6: HTML Report Renderer

41. Create the Jinja2 report template with autoescaping enabled.
42. Render the `Locator Lense` header and page information:
   - Page title.
   - Final resolved URL when applicable.
   - Detected technology stack.
43. Render the element table with category, normalized text, tag, selected locator, locator type, match count, score, styles, and relevant attributes.
44. Render clear states for:
   - Empty or invalid input.
   - Unavailable URL.
   - No extracted elements.
   - Missing style metadata as `Not available`.
   - Undetected technology as `Not detected`.
   - Non-unique locators.
45. Ensure analyzed titles, text, attributes, URLs, styles, and technology values are HTML-escaped and never rendered as trusted HTML.
46. Connect the Flask route to the full pipeline and return the report in one response.

**Blocked until complete:** End-to-end validation is blocked until fetching, parsing, all analysis passes, locator generation, and rendering are integrated.

## 3. One-Day MVP Priorities

### Must Complete

- Project setup and dependency pinning.
- Exactly-one-input validation.
- Raw HTML analysis.
- HTTP/HTTPS fetching with redirect limit and timeouts.
- Shared HTML parsing.
- Required visible element extraction and text normalization.
- Inline and directly retrievable linked CSS style metadata.
- Deterministic locators with fixed scores and uniqueness rules.
- Page metadata and element table report.
- Safe HTML encoding.
- Focused automated tests and manual smoke validation.

### Simplify Without Removing

- Use a small documented technology-signature registry.
- Support a bounded static CSS selector subset and return `Not available` when unsupported.
- Keep CSS cascade handling limited to reliably resolvable declarations.
- Keep the report server-rendered with minimal styling.

## 4. Explicitly Blocked or Deferred Work

- Style Resolver implementation is blocked until one CSS parser is selected and pinned.
- Locator generation is blocked until the canonical DOM and CSS/XPath match-count approach are fixed.
- Report rendering is blocked until shared analysis result models exist.
- End-to-end tests are blocked until the full request pipeline is connected.
- SSRF protections, advanced resource limits, rate limiting, authentication, background processing, production observability, browser rendering, and JavaScript execution are deferred to a future release.

## 5. Testing and Validation

Complete these tasks after implementation and integration:

1. Test empty input and both-input rejection.
2. Test valid HTTP and HTTPS URL validation and unsupported schemes.
3. Mock successful redirects and verify the final resolved URL appears in the report.
4. Mock redirect-limit and connect/read-timeout failures and verify graceful error output.
5. Test raw HTML parsing, malformed HTML, and no-element pages.
6. Test headings, ARIA headings, interactables, ARIA roles, `tabindex >= 0`, deduplication, and visible-only rules.
7. Test whitespace trimming and collapsing for visible text.
8. Test inline, embedded, linked, unavailable, conflicting, and unsupported CSS values.
9. Test technology detection and the `Not detected` fallback.
10. Test unique and duplicate `id`, `name`, and `data-testid` values.
11. Test CSS selector stability, XPath fallback, match counts, fixed scores, deterministic tie-breaking, and `Non-Unique` marking.
12. Test report rendering with missing metadata and no extracted elements.
13. Test HTML encoding using script tags and event-handler payloads in page titles, text, attributes, URLs, and style values.
14. Run an end-to-end raw HTML submission test and a mocked URL submission test.
15. Perform manual smoke tests with a simple page, a form-heavy page, and a page containing linked CSS.
16. Run formatting/lint checks if configured and confirm the Git diff contains only intended implementation files.

## 6. MVP Completion Gate

The MVP is ready for local/demo use when:

- Both input modes work and exactly-one-input validation is enforced.
- Static required elements are extracted once with normalized text.
- Final URL, page title, styles, technology status, and element metadata appear in the report.
- Each element has a deterministic preferred locator with correct uniqueness marking and score.
- Redirects are bounded and request timeouts prevent indefinite waits.
- Error and empty states render without unhandled exceptions.
- Untrusted analyzed values are safely encoded in the report.
- The focused test suite and manual smoke tests pass.
