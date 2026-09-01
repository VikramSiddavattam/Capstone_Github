# Locator Lense MVP Architecture

## 1. Architecture Summary

Locator Lense is implemented as a single-process, stateless web application. A user
submits a webpage URL or raw HTML through a simple form. The backend fetches the
page (if a URL was given), parses the static HTML DOM, runs a series of read-only
analysis passes (element extraction, style resolution, locator generation, technology
detection), and renders the results into an HTML report returned in the same
request/response cycle.

There is no database, background job queue, or authentication layer. Every
submission is analyzed independently and nothing is persisted between requests,
keeping the MVP simple and easy to reason about.

## 2. Key Components and Responsibilities

1. **Web Layer (Flask routes)**
   - Serves the input form (URL or raw HTML textarea).
   - Enforces "exactly one input source" validation and rejects invalid combinations.
   - Handles empty/invalid input and errors gracefully, returning a usable error report
     instead of an unhandled failure.
   - Invokes the analysis pipeline and returns the rendered report.

2. **Fetcher**
   - Resolves URL inputs via an HTTP client (`requests`).
   - Accepts only syntactically valid `http` and `https` URLs.
   - Follows standard HTTP redirects automatically and captures the final resolved URL.
   - Limits the number of redirects and applies explicit connect/read timeouts.
   - Marks a URL unavailable only when the final destination cannot be reached or
     returns an error.
   - Fetches directly linked CSS resources (`<link rel="stylesheet">`) referenced in
     the HTML, when reachable.

3. **HTML Parser**
   - Parses the retrieved/raw HTML into a single DOM tree using BeautifulSoup/lxml.
   - Tolerant of malformed HTML so downstream analysis does not break.
   - Produces the shared parse tree used by all analyzer components below.

4. **Element Extractor**
   - Walks the DOM applying the extraction rules: headings (`h1`â€“`h6`, ARIA heading
     roles), interactable elements (links, buttons, inputs, selects, textareas,
     ARIA roles, `tabindex >= 0`).
   - Deduplicates elements that match multiple rules so each is reported once.
   - Determines visibility using statically available HTML/CSS cues.
   - Normalizes visible text (trim + collapse whitespace).

5. **Style Resolver**
   - Combines inline `style` attributes with parsed rules from `<style>` blocks and
     directly retrieved linked CSS to determine font family, font size, and text color.
   - Does not implement a full cascade/inheritance/computed-style engine.
   - Falls back to `Not available` when a value cannot be reliably determined.

6. **Locator Generator**
   - Computes candidate locators per element: `id`, `name`, `data-testid`,
     XPath, CSS Selector, in that preference order.
   - Checks uniqueness (match count) against the complete analyzed DOM.
   - Applies fixed base scores (id 100, name 90, data-testid 85, CSS 75, XPath 65),
     prefers unique locators, and marks non-unique ones accordingly.
   - Generates deterministic relative XPath candidates before CSS candidates,
     preferring unique stable attributes, normalized visible text, and stable
     axis expressions such as `ancestor::`, `descendant::`, `following-sibling::`,
     and `preceding-sibling::`. Avoids absolute root-based paths by default and
     uses positional indexes only as a final fallback within a stable container.
   - Generates CSS candidates with stable attributes and short unique structural
     selectors while avoiding volatile class names where possible.
   - Selects and reports a single preferred locator per element (no alternatives).

7. **Technology Stack Detector**
   - Best-effort signature detection using signals available in the supplied HTML
     and directly available page resources (e.g., meta generator tags, script/link
     patterns, common framework fingerprints).
   - Returns `Not detected` when no signal matches.

8. **Report Renderer**
   - Assembles all analysis output into the `Locator Lense` HTML report using a
     server-side template (Jinja2).
   - Displays page info (title, final resolved URL, detected tech stack), and a
     table of extracted elements with their metadata, with visible text shown before
     category.
   - Clearly flags missing metadata, unavailable URLs, no matching elements, and
     non-unique locators.
   - HTML-escapes all analyzed values through template autoescaping; analyzed page
     content is never rendered as trusted HTML.

## 3. Data Flow

```
Browser (form submission: URL or raw HTML)
        â”‚
        â–¼
Flask route (input validation)
        â”‚
        â–¼
Fetcher (only if URL input) â”€â”€ resolves redirects, captures final URL/status
        â”‚
        â–¼
HTML Parser (builds shared DOM tree)
        â”‚
        â”œâ”€â”€â–¶ Element Extractor â”€â”€â”€â”€â”
        â”œâ”€â”€â–¶ Style Resolver â”€â”€â”€â”€â”€â”€â”€â”¤ (read-only passes over the same DOM)
        â””â”€â”€â–¶ Tech Stack Detector â”€â”€â”˜
        â”‚
        â–¼
Locator Generator (uses extracted elements + full DOM for match counts)
        â”‚
        â–¼
Report Renderer (Jinja2 template â†’ HTML report)
        â”‚
        â–¼
HTTP response â†’ Browser (renders report in-browser)
```

All processing happens within a single request/response cycle; no intermediate
state is persisted.

## 4. Recommended Technology Choices

| Concern              | Choice                          | Justification |
|-----------------------|----------------------------------|----------------|
| Web framework          | Flask                           | Minimal boilerplate, well suited for a small synchronous MVP with a simple form + report view. |
| HTML parsing            | BeautifulSoup + lxml            | Tolerant of malformed markup; good CSS-selector support via `soupsieve`; widely used and well documented. |
| HTTP client            | `requests`                      | Simple, reliable handling of redirects, timeouts, and error responses. |
| CSS parsing            | `tinycss2` / `cssutils`          | Lightweight parsing of inline/linked CSS declarations without a full browser rendering engine, keeping analysis static-only. |
| Templating             | Jinja2 (bundled with Flask)      | Server-side rendering of the HTML report without needing a separate frontend framework. |
| Persistence            | None                             | MVP is stateless by design; no history or storage requirement. |
| JS execution            | None (explicitly excluded)       | Out of scope; static HTML DOM analysis only. |

## 5. Assumptions and Constraints

1. Single-page, single-request analysis only â€” no crawling, authentication, or history.
2. Linked CSS is fetched only from directly reachable URLs referenced in the HTML;
   unreachable resources degrade gracefully to `Not available`.
3. No JavaScript execution; dynamically injected content and fully computed styles
   are out of scope.
4. Deployed as a simple single-instance application; no scaling, queueing, or
   background workers are required for the MVP.
5. Payload size is constrained by basic request size limits rather than a specific
   numeric requirement.
6. Cross-domain iframe content is not analyzed.

7. Static visibility uses only reliable HTML/CSS cues such as `hidden`,
  `aria-hidden="true"`, `display:none`, and `visibility:hidden`; layout-dependent
  visibility is not inferred.
8. The selected CSS parser and direct dependency versions shall be fixed before
  implementation for reproducible local setup.

## 6. MVP Review Decisions

This is a local/demo MVP. The implementation shall include basic URL validation,
a fixed redirect limit, explicit request timeouts, deterministic locator generation,
and safe HTML encoding in the report.

SSRF protection, advanced resource controls, rate limiting, production observability,
authentication, background processing, and other deployment hardening are deferred
to a future release.

## 7. Risks, Gaps, and Trade-offs

- **Style accuracy**: Without a full CSS cascade/inheritance engine, some computed
  styles may be approximated or reported as `Not available`. Acceptable for the MVP
  but a known limitation.
- **Technology detection accuracy**: Signature-based detection is best-effort and
  may miss or misidentify frameworks; `Not detected` is an explicitly allowed outcome.
- **Visibility detection**: Determining visibility from static HTML/CSS alone (no
  layout engine) is heuristic and may misjudge complex CSS-driven visibility.
- **Performance**: Fetching multiple linked CSS resources adds latency; requires
  sane timeouts to avoid slow report generation.
- **Synchronous request/response**: Large pages may feel slow to the user; accepted
  as a reasonable trade-off for MVP simplicity over introducing async processing
  or job queues.

<!-- BEGIN AUTO-GENERATED DOCUMENTATION SYNC -->

## Automated Documentation Sync

- Generated by .github/hooks/scripts/notify-doc-update.ps1.
- Latest impacted change signals: code.
- Sync action: ag/project-intelligence.md regenerated from current repository context.
- Confidence: medium - code changed; architectural meaning requires review.
- Manual intervention: review this artifact if the change altered business behavior, architecture, acceptance criteria, external integrations, quality gates, or known limitations.

<!-- END AUTO-GENERATED DOCUMENTATION SYNC -->
