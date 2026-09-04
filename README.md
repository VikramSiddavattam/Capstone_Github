# Locator Lense

Locator Lense is a local/demo Flask MVP that analyzes a webpage URL or raw HTML and
generates an HTML report containing visible headings, subheadings, interactable
elements, static style metadata, technology signals, and preferred locators.

The application analyzes the server-delivered HTML DOM only. It does not execute
JavaScript or render pages in a browser.

## Features

- Accepts exactly one input source: an `http://` or `https://` URL, or raw HTML.
- Follows redirects up to the configured limit and reports the final URL.
- Uses a 5-second connect timeout and 10-second read timeout.
- Parses malformed HTML with BeautifulSoup and lxml.
- Extracts visible headings, subheadings, links, buttons, inputs, selects,
  textareas, supported ARIA roles, and elements with `tabindex >= 0`.
- Deduplicates elements that match multiple extraction rules.
- Normalizes visible text by trimming it and collapsing consecutive whitespace.
- Excludes static `hidden`, `aria-hidden="true"`, `display:none`, and
  `visibility:hidden` elements.
- Reads font family, font size, and text color from inline styles, embedded style
  blocks, and directly retrievable linked stylesheets.
- Detects common technology signatures on a best-effort basis.
- Generates one deterministic preferred locator per element.
- Escapes analyzed values safely in the generated report.

## Requirements

- Windows PowerShell or an equivalent shell.
- Python 3.14 or a compatible Python version.
- Internet access is needed only for URL analysis or linked CSS retrieval.

## Setup

Create the project virtual environment and install the pinned dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

To activate the environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Primary dependencies are Flask, Requests, BeautifulSoup, lxml, tinycss2, and pytest.

## Run the Application

Start the local Flask server:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in a browser.

Routes:

- `GET /` displays the input form.
- `POST /analyze` validates the input, analyzes the page, and returns the report.

Submit either a URL or raw HTML. Providing neither input or providing both inputs
returns a validation error.

## Report Contents

The report header displays `Locator Lense` and includes:

- Page title.
- Final resolved URL for URL analysis.
- Detected technology or `Not detected`.
- A table containing normalized text, category, tag name, selected locator, locator
  type, match count, score, styles, and relevant attributes.

Missing style values are shown as `Not available`. Empty reports state when no
matching visible elements were found. Failed URL requests display a readable error.

## Locator Rules

The generator evaluates locators in this priority order:

1. `id` - score `100`.
2. `name` - score `90`.
3. `data-testid` - score `85`.
4. XPath - score `65`.
5. CSS Selector - score `75`.

Unique locators are always preferred. If no unique locator exists, the generator
selects the highest-priority locator type and then the candidate with the lowest
match count within that type. Non-unique selections retain their base score and are
marked `Non-Unique` in the report.

XPath candidates are relative and are preferred over CSS when both are unique. They
rank stable attributes, normalized text, stable `ancestor::`, `descendant::`,
`following-sibling::`, and `preceding-sibling::` axis expressions, and finally
positional indexes within a stable container. CSS selectors remain the final fallback
and prefer stable attributes and short structural selectors while avoiding volatile
class names where possible.

## Static Analysis Limitations

The MVP intentionally does not provide browser-rendered analysis:

- JavaScript is not executed.
- Dynamically injected content is excluded.
- CSS is not fully computed through a browser layout engine.
- Inheritance and complex layout-dependent visibility are not inferred.
- Uncertain style values are reported as `Not available`.
- Technology detection is signature-based and may return `Not detected`.

## Testing

Run the complete unit, integration, regression, and document verification suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The suite covers parsing, URL validation, timeouts, redirects, linked CSS, element
extraction, visibility, normalization, styles, technology detection, locator rules,
report flows, missing data, invalid input, error handling, HTML escaping, and the
required sections of `requirements.md`, `architecture.md`, and `impl-plan.md`.

For dependency vulnerability auditing:

```powershell
.\.venv\Scripts\python.exe -m pip install pip-audit
.\.venv\Scripts\python.exe -m pip_audit -r requirements.txt
```

For linting (matches the `quality-gate` CI check):

```powershell
.\.venv\Scripts\python.exe -m pip install flake8
.\.venv\Scripts\python.exe -m flake8 . --max-line-length=100
```

## Continuous Integration

GitHub Actions workflows in `.github/workflows/` enforce the Development, Code
Review, Verification, and Pull Request phases with automated evidence:

- `ci.yml` runs the full pytest suite on every push and pull request to `main`.
- `quality-gate.yml` runs `flake8` and the full test suite as a required pull
  request check, uploading test results as an artifact.
- `codeql.yml` runs CodeQL static security analysis on pushes, pull requests, and
  a weekly schedule.

## Development Workflow (Agentic SDLC)

This project was built using a Copilot-driven, agent-based SDLC workflow defined
under `.github/`:

- `.github/copilot-instructions.md` — repository-wide standards applied to every phase.
- `.github/agents/*.agent.md` — one subagent per SDLC role (Requirements,
  Architecture, Design Review, Implementation Plan, Development, Code Review,
  Verification, PR).
- `.github/skills/<name>/SKILL.md` — reusable expertise shared across agents
  (`requirements-analysis`, `architecture-design`, `review`, `verification`).
- `.github/prompts/orchestrator.prompt.md` — the single entry point that
  sequences all agents end-to-end, with retry loops for failed reviews/verification.
- `.github/hooks/` — deterministic reminder to keep `documentation/*.md` in sync
  when `locator_lense/` source changes.

Each phase's output is a versioned artifact under `documentation/` (see below),
giving full traceability from requirements to the pull request description.

## Project Structure

```text
app.py                         Flask entry point and pipeline orchestration
locator_lense/
  config.py                    MVP constants and locator scores
  extractor.py                 Visible element extraction and normalization
  fetcher.py                   URL and stylesheet retrieval
  locators.py                  Deterministic locator generation
  models.py                    Shared result models
  parser.py                    BeautifulSoup/lxml parsing helpers
  styles.py                    Static CSS style resolution
  technology.py                Technology detection
templates/
  index.html                   Input form
  report.html                  HTML analysis report
tests/                          Unit, integration, and QA verification tests
documentation/
  requirements.md              Approved product requirements
  architecture.md              Approved MVP architecture
  design-review.md             Architecture review decisions
  impl-plan.md                 Dependency-ordered implementation plan
  project-history.html         Project history and screenshots
  screenshots/                 Application and report screenshots
rag/
  project-intelligence.md      AI retrieval source for app, architecture, and SDLC context
.github/
  copilot-instructions.md      Repository-wide SDLC standards
  agents/                      One *.agent.md subagent per SDLC role
  skills/                      Reusable SKILL.md expertise shared across agents
  prompts/                     orchestrator.prompt.md end-to-end entry point
  hooks/                       Deterministic doc-sync reminder automation
  workflows/                   CI, quality-gate, and CodeQL GitHub Actions
```

## MVP Scope and Deferred Work

This is a local/demo application. The following items are intentionally deferred:

- SSRF protection and private-network blocking.
- Advanced response, DOM, CSS, and processing resource controls.
- Rate limiting and abuse prevention.
- Authentication and authorization.
- Background jobs, queues, and scaling.
- Browser rendering and JavaScript execution.
- Full CSS cascade and computed-style evaluation.
- Full website audits, crawling, screenshots, accessibility scoring, and cross-domain
  iframe analysis.

Do not use the Flask development server as a production deployment.

## Knowledge Base (RAG)

The repository maintains a lightweight Retrieval-Augmented Generation (RAG) source under:

```text
rag/
  project-intelligence.md
```

## Memory Layer

The repository includes a lightweight memory layer that stores learned context, historical decisions, and analysis outcomes beyond source code and documentation retrieval.

```text
memory/
├── user-profile.json
├── project-memory.json
└── analysis-history.json
```
