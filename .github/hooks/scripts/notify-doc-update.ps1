# PostToolUse hook: after relevant edits, refresh generated documentation
# intelligence and mark SDLC artifacts that need semantic review.
$ErrorActionPreference = 'Stop'

try {
    $inputJson = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($inputJson)) { exit 0 }
    $data = $inputJson | ConvertFrom-Json
} catch {
    # Malformed/absent input must never block the agent session.
    exit 0
}

# Only react to tools that create or modify files.
$editTools = @('editFiles', 'createFile', 'create_file', 'replace_string_in_file', 'multi_replace_string_in_file', 'insert_edit_into_file', 'apply_patch')
if ($data.tool_name -and ($editTools -notcontains $data.tool_name)) {
    exit 0
}

$toolInputText = $data.tool_input | ConvertTo-Json -Compress
if (-not $toolInputText) { exit 0 }

$normalizedToolInput = $toolInputText.Replace('\\', '/')

$signalList = [System.Collections.Generic.List[string]]::new()
if ($normalizedToolInput.Contains('app.py') -or $normalizedToolInput.Contains('locator_lense/') -or $normalizedToolInput.Contains('templates/')) { $signalList.Add('code') }
if ($normalizedToolInput.Contains('tests/')) { $signalList.Add('tests') }
if ($normalizedToolInput.Contains('documentation/requirements.md')) { $signalList.Add('requirements') }
if ($normalizedToolInput.Contains('documentation/architecture.md')) { $signalList.Add('architecture') }
if ($normalizedToolInput.Contains('documentation/impl-plan.md')) { $signalList.Add('planning') }
if ($normalizedToolInput.Contains('documentation/code-review.md') -or $normalizedToolInput.Contains('documentation/design-review.md')) { $signalList.Add('review') }
if ($normalizedToolInput.Contains('documentation/verification-report.md')) { $signalList.Add('verification') }
if ($normalizedToolInput.Contains('documentation/pr-description.md')) { $signalList.Add('pr') }
if ($normalizedToolInput.Contains('.github/') -or $normalizedToolInput.Contains('.vscode/')) { $signalList.Add('workflow') }
if ($normalizedToolInput.Contains('README.md')) { $signalList.Add('readme') }
if ($normalizedToolInput.Contains('rag/project-intelligence.md')) { $signalList.Add('intelligence') }

if ($signalList.Count -eq 0) { exit 0 }
$signals = $signalList.ToArray()

function GetDependencyBullets {
    if (-not (Test-Path -LiteralPath 'requirements.txt' -PathType Leaf)) {
        return '- Dependencies not found; `requirements.txt` is missing.'
    }
    $lines = Get-Content -LiteralPath 'requirements.txt' | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    if ($lines.Count -eq 0) { return '- No pinned dependencies found.' }
    return (($lines | ForEach-Object { "- $_" }) -join [Environment]::NewLine)
}

function GetPathMap {
    $entries = @(
        'app.py                         Flask entry point and analysis pipeline orchestration',
        'locator_lense/config.py        Constants: locator priority/scores, redirect limit, request timeouts',
        'locator_lense/models.py        Immutable result contracts used by the pipeline',
        'locator_lense/fetcher.py       URL validation, HTML fetch, redirects, timeouts, linked CSS fetch',
        'locator_lense/parser.py        BeautifulSoup/lxml parsing and title extraction',
        'locator_lense/extractor.py     Visible element extraction, category assignment, text normalization',
        'locator_lense/styles.py        Static CSS style parsing and supported metadata resolution',
        'locator_lense/technology.py    Best-effort technology signature detection',
        'locator_lense/locators.py      Locator candidate generation, matching, scoring, tie-breaking',
        'templates/index.html           Input form',
        'templates/report.html          HTML analysis report',
        'tests/                         Automated parser, fetcher, locator, app-flow, and QA verification tests',
        'documentation/                 SDLC requirements, architecture, review, implementation, verification, and PR artifacts',
        'rag/project-intelligence.md    Concise AI retrieval source generated from current repo context',
        '.github/                       Copilot SDLC agents, skills, prompts, hooks, and GitHub Actions',
        '.vscode/                       Project editor, debug, task, extension, and MCP configuration'
    )
    return ($entries -join [Environment]::NewLine)
}

function NewProjectIntelligence {
    $dependencies = GetDependencyBullets
    $pathMap = GetPathMap
    return @"
# Locator Lense Project Intelligence

<!-- BEGIN AUTO-GENERATED PROJECT INTELLIGENCE -->
Generated from the current repository sources, README, and SDLC artifacts. Preserve human notes outside this generated block.

## Application Overview

Locator Lense is a local/demo Flask MVP that analyzes either a webpage URL or raw HTML and renders an HTML report of static DOM elements, style metadata, technology signals, and deterministic preferred locators. It analyzes server-delivered HTML only; it does not execute JavaScript or render pages in a browser.

## Business Purpose

The application helps QA engineers, test automation developers, and reviewers inspect a page's static structure and identify stable locators for headings, subheadings, and interactable elements. Its value is fast local analysis, deterministic locator output, and traceable MVP validation.

## Architecture Summary

The app is a single-process, stateless Flask service. Users submit exactly one input source: an `http://` or `https://` URL, or raw HTML. URL inputs are fetched with bounded redirects and explicit connect/read timeouts. Raw or fetched HTML is parsed into a BeautifulSoup/lxml DOM, then independent read-only passes extract elements, resolve static styles, detect technology, generate preferred locators, and render a Jinja2 report.

No database, authentication layer, queue, background worker, browser renderer, or persisted state is used. Each submission is processed independently in one request/response cycle.

## Technology Stack

$dependencies
- GitHub Actions for CI, quality gate, and CodeQL security scanning
- VS Code/Copilot custom agents, skills, prompt files, hooks, and MCP configuration for SDLC governance

## Feature Catalog

- Accepts exactly one input source: URL or raw HTML.
- Validates URL syntax and supports only HTTP/HTTPS schemes.
- Follows redirects up to the configured limit and reports the final resolved URL.
- Uses explicit request timeouts: 5-second connect timeout, 10-second read timeout.
- Parses malformed HTML into a usable DOM when possible.
- Extracts visible headings, ARIA headings, links, buttons, inputs, selects, textareas, supported ARIA roles, and elements with `tabindex >= 0`.
- Deduplicates elements matching multiple extraction rules.
- Normalizes visible text by trimming and collapsing whitespace.
- Excludes statically hidden elements using `hidden`, `aria-hidden="true"`, `display:none`, and `visibility:hidden` cues.
- Resolves font family, font size, and text color from inline styles, embedded CSS, and directly retrievable linked stylesheets.
- Detects React, Vue, Angular, Bootstrap, WordPress, and generator metadata on a best-effort basis.
- Generates one preferred locator per element using `id`, `name`, `data-testid`, XPath, then CSS Selector priority.
- Prefers unique locators and marks non-unique selected locators as `Non-Unique`.
- Renders safe HTML reports with Jinja2 autoescaping and clear empty/error/missing-data states.

## Source Code Map

```text
$pathMap
```

## Key Modules and Responsibilities

- `app.py`: validates input, orchestrates the analysis pipeline, and renders graceful reports.
- `Fetcher`: validates HTTP/HTTPS URLs, enforces redirect and timeout bounds, captures final URL, and retrieves linked CSS.
- `parser`: creates the shared DOM and extracts page title with malformed-HTML tolerance.
- `extractor`: applies static visibility rules, extracts target elements, deduplicates records, and normalizes text.
- `styles`: resolves supported static style metadata and uses `Not available` when reliable static resolution is not possible.
- `technology`: scans markup/resources for deterministic technology signatures and falls back to `Not detected`.
- `locators`: generates candidates, computes DOM match counts, applies priority/scores, and selects one deterministic locator.
- `models`: defines shared immutable result contracts.

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
- Static CSS support is bounded; uncertain values become `Not available`.
- Technology detection is signature-based and may return `Not detected`.
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

- Requirements source: `documentation/requirements.md`.
- Architecture source: `documentation/architecture.md`.
- Review source: `documentation/code-review.md` and `documentation/design-review.md`.
- Verification source: `documentation/verification-report.md`.
- PR source: `documentation/pr-description.md`.
- Automation source: `.github/hooks/scripts/notify-doc-update.ps1`.

<!-- END AUTO-GENERATED PROJECT INTELLIGENCE -->

## Human-Maintained Notes

Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.
"@
}

function SetGeneratedProjectIntelligence {
    if (-not (Test-Path -LiteralPath 'rag' -PathType Container)) {
        New-Item -ItemType Directory -Path 'rag' | Out-Null
    }
    $path = 'rag/project-intelligence.md'
    $generated = NewProjectIntelligence
    $start = '<!-- BEGIN AUTO-GENERATED PROJECT INTELLIGENCE -->'
    $end = '<!-- END AUTO-GENERATED PROJECT INTELLIGENCE -->'

    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $existing = Get-Content -LiteralPath $path -Raw
        $prefix = '# Locator Lense Project Intelligence' + [Environment]::NewLine + [Environment]::NewLine
        $suffix = [Environment]::NewLine + '## Human-Maintained Notes' + [Environment]::NewLine + [Environment]::NewLine + 'Add project-specific retrieval notes here if needed. This section is preserved by the synchronization hook.' + [Environment]::NewLine
        $startIndex = $existing.IndexOf($start)
        $endIndex = $existing.IndexOf($end)
        if ($startIndex -ge 0 -and $endIndex -gt $startIndex) {
            $afterIndex = $endIndex + $end.Length
            $prefix = $existing.Substring(0, $startIndex)
            $suffix = $existing.Substring($afterIndex)
        }
        Set-Content -LiteralPath $path -Value ($prefix + ($generated.Substring($generated.IndexOf($start))) + $suffix.TrimStart()) -Encoding UTF8
    } else {
        Set-Content -LiteralPath $path -Value $generated -Encoding UTF8
    }
}

function SetSdlcSyncSection($Path, [string[]]$RelevantImpacts, [string]$Confidence) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    $content = Get-Content -LiteralPath $Path -Raw
    $start = '<!-- BEGIN AUTO-GENERATED DOCUMENTATION SYNC -->'
    $end = '<!-- END AUTO-GENERATED DOCUMENTATION SYNC -->'
    $section = @"
$start

## Automated Documentation Sync

- Generated by `.github/hooks/scripts/notify-doc-update.ps1`.
- Latest impacted change signals: $($RelevantImpacts -join ', ').
- Sync action: `rag/project-intelligence.md` regenerated from current repository context.
- Confidence: $Confidence.
- Manual intervention: review this artifact if the change altered business behavior, architecture, acceptance criteria, external integrations, quality gates, or known limitations.

$end
"@
    $startIndex = $content.IndexOf($start)
    $endIndex = $content.IndexOf($end)
    if ($startIndex -ge 0 -and $endIndex -gt $startIndex) {
        $afterIndex = $endIndex + $end.Length
        $before = $content.Substring(0, $startIndex).TrimEnd()
        $after = $content.Substring($afterIndex).TrimStart()
        $newContent = $before + [Environment]::NewLine + [Environment]::NewLine + $section.TrimEnd()
        if (-not [string]::IsNullOrWhiteSpace($after)) {
            $newContent += [Environment]::NewLine + [Environment]::NewLine + $after.TrimEnd()
        }
        Set-Content -LiteralPath $Path -Value $newContent -Encoding UTF8
    } else {
        $legacyIndex = $content.IndexOf('## Automated Documentation Sync')
        if ($legacyIndex -ge 0) {
            $content = $content.Substring(0, $legacyIndex)
        }
        Set-Content -LiteralPath $Path -Value ($content.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + $section.TrimEnd()) -Encoding UTF8
    }
    return $true
}

$updatedList = [System.Collections.Generic.List[string]]::new()
SetGeneratedProjectIntelligence
$updatedList.Add('rag/project-intelligence.md')

$manualReviewList = [System.Collections.Generic.List[string]]::new()
if ($signals -contains 'code') {
    if (SetSdlcSyncSection 'documentation/architecture.md' $signals 'medium - code changed; architectural meaning requires review') { $updatedList.Add('documentation/architecture.md') }
    if (SetSdlcSyncSection 'documentation/requirements.md' $signals 'medium - behavior may have changed; acceptance criteria require review') { $updatedList.Add('documentation/requirements.md') }
    if (SetSdlcSyncSection 'documentation/impl-plan.md' $signals 'high - implementation artifact availability can be verified deterministically') { $updatedList.Add('documentation/impl-plan.md') }
    $manualReviewList.Add('Confirm whether code/template changes altered behavior, acceptance criteria, architecture, or limitations.')
}
if ($signals -contains 'workflow') {
    if (SetSdlcSyncSection 'documentation/architecture.md' $signals 'medium - workflow/integration governance changed') { $updatedList.Add('documentation/architecture.md') }
    if (SetSdlcSyncSection 'documentation/verification-report.md' $signals 'medium - verification governance may need refreshed evidence') { $updatedList.Add('documentation/verification-report.md') }
    $manualReviewList.Add('Confirm whether workflow, MCP, hook, or CI changes affect governance requirements.')
}
if (($signals -contains 'requirements') -or ($signals -contains 'architecture') -or ($signals -contains 'planning') -or ($signals -contains 'review') -or ($signals -contains 'verification') -or ($signals -contains 'pr') -or ($signals -contains 'readme')) {
    $manualReviewList.Add('Source documentation changed; generated project intelligence was refreshed from current repository context.')
}

$updated = $updatedList.ToArray() | Select-Object -Unique
$manualReview = $manualReviewList.ToArray() | Select-Object -Unique
$summary = "Automated documentation sync completed. Updated: $(($updated) -join ', '). Impact signals: $(($signals | Select-Object -Unique) -join ', ')."
if ($manualReview.Count -gt 0) {
    $summary += " Manual review: $(($manualReview) -join ' ')"
}

$output = [ordered]@{
    hookSpecificOutput = [ordered]@{
        hookEventName      = 'PostToolUse'
        additionalContext  = $summary
    }
}

$output | ConvertTo-Json -Depth 10 -Compress
exit 0
