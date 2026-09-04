# Locator Lense Project Intelligence

<!-- BEGIN AUTO-GENERATED PROJECT INTELLIGENCE -->
Generated from the current repository sources, README, and SDLC artifacts. Preserve human notes outside this generated block.

## Application Overview

Locator Lense is a local/demo Flask MVP that analyzes either a webpage URL or raw HTML and renders an HTML report of static DOM elements, style metadata, technology signals, and deterministic preferred locators. It analyzes server-delivered HTML only; it does not execute JavaScript or render pages in a browser.

## Business Purpose

The application helps QA engineers, test automation developers, and reviewers inspect a page's static structure and identify stable locators for headings, subheadings, and interactable elements. Its value is fast local analysis, deterministic locator output, and traceable MVP validation.

## Architecture Summary

The app is a single-process, stateless Flask service. Users submit exactly one input source: an http:// or https:// URL, or raw HTML. URL inputs are fetched with bounded redirects and explicit connect/read timeouts. Raw or fetched HTML is parsed into a BeautifulSoup/lxml DOM, then independent read-only passes extract elements, resolve static styles, detect technology, generate preferred locators, and render a Jinja2 report.

No database, authentication layer, queue, background worker, browser renderer, or persisted state is used. Each submission is processed independently in one request/response cycle.

## Technology Stack

- Flask==3.1.3
- beautifulsoup4==4.12.3
- lxml==6.1.2
- requests==2.33.0
- tinycss2==1.4.0
- pytest==9.0.3
- GitHub Actions for CI, quality gate, and CodeQL security scanning
- VS Code/Copilot custom agents, skills, prompt files, hooks, and MCP configuration for SDLC governance

## Feature Catalog

- Accepts exactly one input source: URL or raw HTML.
- Validates URL syntax and supports only HTTP/HTTPS schemes.
- Follows redirects up to the configured limit and reports the final resolved URL.
- Uses explicit request timeouts: 5-second connect timeout, 10-second read timeout.
- Parses malformed HTML into a usable DOM when possible.
- Extracts visible headings, ARIA headings, links, buttons, inputs, selects, textareas, supported ARIA roles, and elements with 	abindex >= 0.
- Deduplicates elements matching multiple extraction rules.
- Normalizes visible text by trimming and collapsing whitespace.
- Excludes statically hidden elements using hidden, ria-hidden="true", display:none, and isibility:hidden cues.
- Resolves font family, font size, and text color from inline styles, embedded CSS, and directly retrievable linked stylesheets.
- Detects React, Vue, Angular, Bootstrap, WordPress, and generator metadata on a best-effort basis.
- Generates one preferred locator per element using id, 
ame, data-testid, XPath, then CSS Selector priority.
- Prefers unique locators and marks non-unique selected locators as Non-Unique.
- Renders safe HTML reports with Jinja2 autoescaping and clear empty/error/missing-data states.

## Source Code Map

`	ext
app.py                         Flask entry point and analysis pipeline orchestration
locator_lense/config.py        Constants: locator priority/scores, redirect limit, request timeouts
locator_lense/models.py        Immutable result contracts used by the pipeline
locator_lense/fetcher.py       URL validation, HTML fetch, redirects, timeouts, linked CSS fetch
locator_lense/parser.py        BeautifulSoup/lxml parsing and title extraction
locator_lense/extractor.py     Visible element extraction, category assignment, text normalization
locator_lense/styles.py        Static CSS style parsing and supported metadata resolution
locator_lense/technology.py    Best-effort technology signature detection
locator_lense/locators.py      Locator candidate generation, matching, scoring, tie-breaking
templates/index.html           Input form
templates/report.html          HTML analysis report
tests/                         Automated parser, fetcher, locator, app-flow, and QA verification tests
documentation/                 SDLC requirements, architecture, review, implementation, verification, and PR artifacts
rag/project-intelligence.md    Concise AI retrieval source generated from current repo context
.github/                       Copilot SDLC agents, skills, prompts, hooks, and GitHub Actions
.vscode/                       Project editor, debug, task, extension, and MCP configuration
`

## Key Modules and Responsibilities

- pp.py: validates input, orchestrates the analysis pipeline, and renders graceful reports.
- Fetcher: validates HTTP/HTTPS URLs, enforces redirect and timeout bounds, captures final URL, and retrieves linked CSS.
- parser: creates the shared DOM and extracts page title with malformed-HTML tolerance.
- extractor: applies static visibility rules, extracts target elements, deduplicates records, and normalizes text.
- styles: resolves supported static style metadata and uses Not available when reliable static resolution is not possible.
- 	echnology: scans markup/resources for deterministic technology signatures and falls back to Not detected.
- locators: generates candidates, computes DOM match counts, applies priority/scores, and selects one deterministic locator.
- models: defines shared immutable result contracts.

## Design Decisions

- Keep the MVP stateless and synchronous to avoid unnecessary infrastructure.
- Analyze static HTML only to keep behavior deterministic and lightweight.
- Use explicit redirect and timeout controls to prevent indefinite network waits.
- Prefer one deterministic locator over large alternative locator lists.
- Generate relative XPath before CSS fallback, prioritizing stable attributes, normalized text, axes, and positional fallback only within stable containers.
- Use Jinja2 autoescaping so analyzed page data is never rendered as trusted HTML.
- Preserve traceability through SDLC artifacts and Copilot quality-gate hooks.

## Known Limitations

- JavaScript is not executed; dynamically injected content is excluded.
- Browser-computed styles and layout-dependent visibility are not inferred.
- Static CSS support is bounded; uncertain values become Not available.
- Technology detection is signature-based and may return Not detected.
- Large DOM performance is not explicitly resource-bounded beyond MVP assumptions.
- SSRF protection, private-network blocking, rate limiting, authentication, production observability, and deployment hardening are deferred.
- Redirect-chain reporting is out of scope; only final resolved URL is reported.
- Cross-domain iframe content, crawling, screenshots, accessibility scoring, and full website audits are out of scope.

## Future Enhancements

- Add SSRF protections and private-network address blocking before hosted production deployment.
- Add response-size, DOM-size, CSS-size, and processing-time limits.
- Add structured logging and production observability.
- Add optional browser-rendered analysis for JavaScript-heavy pages.
- Expand CSS cascade/computed-style support.
- Add Unicode locator tests and large-DOM performance benchmarks.
- Add authenticated/private-page analysis only after explicit credential-handling design and security review.
- Add richer technology signatures and confidence scoring.

## SDLC Sync Notes

- Requirements source: documentation/requirements.md.
- Architecture source: documentation/architecture.md.
- Review source: documentation/code-review.md and documentation/design-review.md.
- Verification source: documentation/verification-report.md.
- PR source: documentation/pr-description.md.
- Automation source: .github/hooks/scripts/notify-doc-update.ps1.

<!-- END AUTO-GENERATED PROJECT INTELLIGENCE -->

## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.


















