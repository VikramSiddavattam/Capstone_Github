# Locator Lense MVP Design Review

## Review Scope

Reviewed `architecture.md` against the approved MVP requirements and evaluated requirements coverage, security, error handling, maintainability, performance, testability, dependency safety, and component responsibilities.

## Findings and Recommended Updates

### 1. URL validation and redirect behavior

- **Finding:** The architecture mentions redirects and errors but does not define basic URL validation or a redirect bound.
- **Impact:** Invalid schemes and redirect loops could produce confusing failures or unnecessarily long requests.
- **Recommendation:** Accept only `http` and `https`, validate URL syntax before fetching, follow redirects with a fixed maximum redirect count, and report the final resolved URL.
- **Decision:** Required for the local/demo MVP.

### 2. Request timeouts

- **Finding:** The Fetcher says it applies timeouts but does not define the behavior.
- **Impact:** A slow or unavailable URL could block the synchronous request.
- **Recommendation:** Configure explicit connect and read timeouts and return a clear unavailable/error report when exceeded.
- **Decision:** Required for the local/demo MVP.

### 3. Deterministic locator generation

- **Finding:** The architecture states the locator preference and scores but does not define deterministic candidate selection.
- **Impact:** The same HTML could produce different locators across runs or implementations.
- **Recommendation:** Evaluate candidates in the fixed order `id`, `name`, `data-testid`, XPath, CSS Selector; calculate match counts against the complete DOM; always prefer unique candidates; for non-unique candidates prefer the lowest match count within the highest-priority type; use deterministic tie-breaking and report only the selected locator.
- **Decision:** Required for the local/demo MVP.

### 4. CSS selector stability

- **Finding:** “Shorter/stable” CSS selectors is currently a qualitative statement.
- **Impact:** Generated selectors may be unnecessarily fragile or inconsistent.
- **Recommendation:** Prefer stable attributes, avoid volatile/generated classes where possible, select the shortest candidate that uniquely identifies the element, and use structural selectors only as fallback.
- **Decision:** Required for the local/demo MVP.

### 5. Safe report encoding

- **Finding:** The report includes untrusted page title, text, attributes, URLs, and style values, but safe rendering is not stated.
- **Impact:** Raw HTML input or a fetched page could inject markup or script into the generated report.
- **Recommendation:** Use Jinja2 autoescaping and HTML-encode every analyzed value rendered in the report. Do not render analyzed values as trusted HTML.
- **Decision:** Required for the local/demo MVP.

### 6. Static visibility and style limits

- **Finding:** Visibility and CSS resolution are necessarily heuristic without browser rendering, but the boundary is not explicit enough for consistent implementation.
- **Impact:** Different implementations may disagree about hidden elements or style values.
- **Recommendation:** Use only statically detectable cues such as `hidden`, `aria-hidden="true"`, and directly matched `display:none` or `visibility:hidden` declarations. Mark uncertain style values as `Not available`; do not infer browser-computed or layout-dependent values.
- **Decision:** Required as a documented MVP limitation.

### 7. Dependency selection

- **Finding:** CSS parsing is listed as `tinycss2 / cssutils`, leaving the implementation choice ambiguous.
- **Impact:** Parsing behavior and test results may vary.
- **Recommendation:** Select one CSS parser during implementation and pin direct dependencies for reproducible local setup.
- **Decision:** Required before implementation, without adding unnecessary infrastructure.

### 8. Testing boundaries

- **Finding:** The architecture does not define test seams for network access and analysis passes.
- **Impact:** Deterministic behavior and failure handling will be harder to verify.
- **Recommendation:** Keep the Fetcher, parser, analyzers, locator generator, and renderer callable as separate units. Test network behavior with mocked responses and add focused tests for locators, visibility, normalization, errors, redirects, and HTML encoding.
- **Decision:** Required before production code is considered complete.

## Deferred to a Future Release

The following production-hardening concerns are intentionally deferred because this is a local/demo MVP:

- SSRF protection and private-network address blocking.
- Advanced response, DOM, CSS, and processing resource controls.
- Rate limiting and abuse prevention.
- Authentication and authorization.
- Background jobs, queues, and horizontal scaling.
- Full CSS cascade/computed-style evaluation.
- Browser rendering and JavaScript execution.
- Comprehensive observability and production deployment hardening.

## Review Conclusion

The lightweight single-process architecture is approved for MVP implementation after the agreed clarifications are incorporated into `architecture.md`. The MVP must include basic URL validation, bounded redirects, request timeouts, deterministic locator generation, and safe HTML encoding. Production-hardening controls remain explicitly out of scope for this release.
