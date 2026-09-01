# Locator Lense Project Intelligence

## Application Overview

Locator Lense is a local/demo Flask MVP that analyzes either a webpage URL or raw HTML and renders an HTML report of static DOM elements, styling metadata, detected technology signals, and deterministic preferred locators. It analyzes server-delivered HTML only; it does not execute JavaScript or render pages in a browser.

## Business Purpose

The application helps QA engineers, test automation developers, and reviewers inspect a page's static structure and identify stable locators for headings, subheadings, and interactable elements. Its value is fast local analysis and deterministic locator output for MVP validation, demos, and automation discovery.

## Architecture Summary

The system is a single-process, stateless Flask web app. Users submit exactly one source through the browser: an `http://` or `https://` URL, or raw HTML. URL inputs are fetched with bounded redirects and explicit connect/read timeouts. Raw/fetched HTML is parsed into one BeautifulSoup/lxml DOM, then read-only analysis passes extract elements, resolve static styles, detect technology signatures, generate preferred locators, and render a Jinja2 report.

No database, authentication layer, queue, background worker, browser renderer, or persisted state is used. Every submission is processed independently in one request/response cycle.

## Technology Stack

- Python 3.14-compatible runtime
- Flask 3.1.3 for routing and Jinja2 server-side rendering
- BeautifulSoup 4.12.3 and lxml 6.1.2 for tolerant HTML parsing
- Requests 2.33.0 for URL and linked stylesheet retrieval
- tinycss2 1.4.0 for static CSS declaration parsing
- pytest 9.0.3 for automated unit, integration, regression, and QA verification tests
- GitHub Actions for CI, quality-gate, and CodeQL security scanning
- VS Code/Copilot custom agents, skills, prompts, hooks, and MCP configuration for SDLC governance

## Feature Catalog

- Accepts exactly one input source: URL or raw HTML.
- Validates URL syntax and supports only HTTP/HTTPS schemes.
- Follows redirects up to the configured limit and reports the final resolved URL.
- Uses explicit request timeouts: 5-second connect timeout, 10-second read timeout.
- Parses malformed HTML into a usable DOM when possible.
- Extracts visible headings (`h1`-`h6`, ARIA headings) and interactables (`a`, `button`, `input`, `select`, `textarea`, supported ARIA roles, `tabindex >= 0`).
- Deduplicates elements that match multiple extraction rules.
- Normalizes visible text by trimming and collapsing whitespace.
- Excludes statically hidden elements using `hidden`, `aria-hidden="true"`, `display:none`, and `visibility:hidden` cues.
- Resolves font family, font size, and text color from inline styles, embedded styles, and directly retrievable linked stylesheets.
- Detects React, Vue, Angular, Bootstrap, WordPress, and generator metadata on a best-effort basis.
- Generates one preferred locator per element using `id`, `name`, `data-testid`, XPath, then CSS Selector priority.
- Prefers unique locators; marks non-unique selections as `Non-Unique` while retaining fixed base scores.
- Renders safe HTML reports with Jinja2 autoescaping and clear empty/error/missing-data states.

## Source Code Map

```text
app.py                         Flask entry point and analysis pipeline orchestration
locator_lense/config.py        Constants: locator priority/scores, redirect limit, request timeouts
locator_lense/models.py        Immutable result contracts: FetchResult, ElementRecord, AnalysisResult
locator_lense/fetcher.py       URL validation, HTML fetch, redirect/timeout handling, linked CSS fetch
locator_lense/parser.py        BeautifulSoup/lxml parsing and title extraction
locator_lense/extractor.py     Visible element extraction, category assignment, text normalization
locator_lense/styles.py        Static CSS style parsing and supported metadata resolution
locator_lense/technology.py    Deterministic best-effort technology signature detection
locator_lense/locators.py      Locator candidate generation, matching, scoring, tie-breaking
templates/index.html           Input form
templates/report.html          Report rendering
tests/                         Automated coverage for parser/fetcher, locators, app flows, QA verification
documentation/                 SDLC artifacts: requirements, architecture, design review, implementation plan, review, verification, PR
.github/                       Copilot SDLC agents, skills, orchestrator prompt, hooks, and GitHub Actions workflows
.vscode/                       Project-specific editor, task, debug, extension, and MCP configuration
```

## Key Modules and Responsibilities

- `app.py`: validates exactly-one-input submissions, connects fetching/parsing/analysis/locator/report steps, and returns error reports instead of unhandled failures.
- `Fetcher`: accepts only HTTP/HTTPS URLs, enforces bounded redirects and timeouts, captures final URL, and fetches directly linked CSS when available.
- `parser`: builds the shared DOM and extracts page title with malformed-HTML tolerance.
- `extractor`: applies static visibility rules, extracts headings/interactables, deduplicates records, and normalizes text.
- `styles`: resolves supported static style values and returns `Not available` when reliable static resolution is not possible.
- `technology`: scans HTML and linked CSS for deterministic technology signatures and falls back to `Not detected`.
- `locators`: builds deterministic candidates, computes match counts against the DOM, prefers uniqueness, applies fixed scores, and selects one preferred locator.
- `models`: defines shared immutable data contracts used across the pipeline and tests.

## Design Decisions

- Keep the MVP stateless and synchronous to avoid unnecessary infrastructure.
- Analyze static HTML only; exclude JavaScript execution and browser-rendered DOM to keep behavior deterministic and lightweight.
- Use explicit redirect and timeout controls to prevent indefinite network waits.
- Prefer deterministic locator selection over exhaustive locator alternatives.
- Generate relative XPath before CSS fallback, prioritizing stable attributes, normalized text, stable axes, and only then positional indexes within stable containers.
- Use Jinja2 autoescaping so analyzed page data is never rendered as trusted HTML.
- Keep production hardening deferred but documented: SSRF protection, rate limiting, observability, authentication, and resource controls are out of MVP scope.
- Use SDLC artifacts and Copilot quality-gate hooks to preserve traceability from requirements through PR readiness.

## Known Limitations

- JavaScript is not executed; dynamically injected content is excluded.
- Browser-computed styles and layout-dependent visibility are not inferred.
- Static CSS support is intentionally bounded; uncertain values become `Not available`.
- Technology detection is signature-based and may return `Not detected`.
- Large DOM performance is not explicitly resource-bounded beyond MVP assumptions.
- SSRF protection, private-network blocking, rate limiting, authentication, production observability, and deployment hardening are deferred.
- Redirect-chain reporting is out of scope; only final resolved URL is reported.
- Cross-domain iframe content, crawling, screenshots, accessibility scoring, and full website audits are out of scope.

## Future Enhancements

- Add SSRF protections and private-network address blocking before any hosted production deployment.
- Add response-size, DOM-size, CSS-size, and processing-time limits for stronger resource control.
- Add structured logging and production observability.
- Add optional browser-rendered analysis mode for JavaScript-heavy pages.
- Expand CSS cascade/computed-style support when accuracy matters more than MVP simplicity.
- Add broader internationalized text and Unicode locator test coverage.
- Add large-DOM performance benchmarks and threshold-based CI checks.
- Add authenticated/private-page analysis only with explicit credential-handling design and security review.
- Add richer technology signature registry and confidence scoring.

## Maintenance Notes for AI Agents

- Refresh this document when README, `documentation/*.md`, `app.py`, `locator_lense/*.py`, `templates/*.html`, `tests/*.py`, `.github/`, or `.vscode/` changes in a way that affects behavior, architecture, governance, or developer workflow.
- Keep sections concise and factual; prefer stable project facts over detailed implementation walkthroughs.
- Do not include secrets, access tokens, private customer data, or transient terminal output.
