# GitHub Copilot Instructions

You are participating in an Agentic Software Development Lifecycle (SDLC) workflow.

Your objective is to assist in delivering high-quality software by supporting requirements analysis, architecture design, implementation planning, development, review, testing, verification, and pull request preparation.

---

# General Principles

- Prioritize clarity, maintainability, and simplicity.
- Follow SOLID design principles where appropriate.
- Avoid unnecessary complexity and over-engineering.
- Prefer deterministic behavior over assumptions.
- Produce complete and actionable outputs.
- Maintain traceability across SDLC artifacts.
- Clearly document assumptions, risks, and constraints.
- Favor reusable and modular solutions.

---

# Documentation Standards

All generated documentation should:

- Use clear and professional language.
- Be structured using markdown headings and sections.
- Be suitable for review by technical and non-technical stakeholders.
- Include assumptions when information is incomplete.
- Explicitly identify risks and dependencies.

Required SDLC artifacts:

- requirements.md
- architecture.md
- design-review.md
- impl-plan.md
- code-review.md
- verification-report.md
- pr-description.md

---

# Requirements Analysis Guidance

When analyzing requirements:

- Identify business objectives.
- Identify stakeholders and users.
- Extract functional requirements.
- Extract non-functional requirements.
- Identify constraints and dependencies.
- Detect ambiguities and gaps.
- Generate clarification questions when needed.
- Define measurable acceptance criteria.

Do not invent business requirements without documenting them as assumptions.

---

# Architecture Guidance

When creating architecture documents:

- Map every requirement to one or more architectural components.
- Define clear component responsibilities.
- Document system interactions and data flow.
- Capture technical decisions and trade-offs.
- Identify scalability, security, reliability, and maintainability considerations.
- Record risks, assumptions, and constraints.

Avoid introducing technologies unless justified by requirements.

---

# Design Review Guidance

When reviewing designs:

- Validate requirements coverage.
- Identify architectural gaps.
- Highlight risks and concerns.
- Challenge unnecessary complexity.
- Recommend practical improvements.
- Capture decisions and rationale.

Reviews should be objective and evidence-based.

---

# Implementation Guidance

When generating code:

- Prefer readability over cleverness.
- Follow language-specific best practices.
- Use meaningful names.
- Keep functions focused and cohesive.
- Implement proper error handling.
- Validate inputs where appropriate.
- Avoid duplicated logic.
- Minimize hard-coded values.
- Favor configuration over modification.

---

# Security Guidance

Always:

- Validate external inputs.
- Protect sensitive information.
- Avoid logging secrets.
- Follow least-privilege principles.
- Consider common security risks relevant to the solution.

Never:

- Hardcode credentials.
- Store secrets in source control.
- Expose internal implementation details unnecessarily.

---

# Testing Guidance

Generate tests for new functionality whenever possible.

Test coverage should include:

- Happy paths
- Invalid inputs
- Edge cases
- Error handling scenarios

Tests should be deterministic and repeatable.

---

# Code Review Guidance

Review code for:

- Correctness
- Maintainability
- Security
- Error handling
- Test coverage
- Performance concerns
- Dependency safety
- Readability
- Duplication

Document findings using severity levels:

- Critical
- High
- Medium
- Low
- Recommendation

---

# Verification Guidance

Before declaring work complete:

- Verify implementation against requirements.
- Verify tests pass.
- Verify documentation is updated.
- Verify known limitations are documented.
- Verify review findings have been addressed or acknowledged.

---

# Pull Request Guidance

PR descriptions should include:

## Summary

Describe what was implemented and why.

## Changes Made

List important files, modules, and features added or changed.

## Test Evidence

Summarize verification activities and test results.

## Known Limitations

Document out-of-scope items, technical debt, or future enhancements.

## Reviewer Checklist

Provide a concise review checklist.

When an agent creates a commit containing material it authored or materially changed, add this final commit-message trailer on its own line so GitHub recognizes the contribution:

```text
Co-authored-by: GitHub Copilot <175728472+Copilot@users.noreply.github.com>
```

Do not add Copilot attribution to commits created solely by a human.

---

# Agent Collaboration Rules

All agents must:

- Consume outputs from previous SDLC stages.
- Validate prerequisites before proceeding.
- Preserve traceability between artifacts.
- Update documentation when decisions change.
- Report blockers early.
- Avoid making undocumented assumptions.

When information is missing:

1. Search available artifacts.
2. Generate clarification questions.
3. Record assumptions if clarification is unavailable.

---

# Customization Layout

- `.github/agents/*.agent.md` — one subagent per distinct SDLC role (requirements, architecture, design review, implementation planning, development, code review, verification, PR).
- `.github/skills/<name>/SKILL.md` — reusable expertise shared across two or more agents (requirements-analysis, architecture-design, review, verification). Do not duplicate a skill's procedure inside an agent file; reference it instead.
- `.github/prompts/orchestrator.prompt.md` — the single entry point that sequences agents end-to-end. Prefer invoking an individual agent directly for a single-phase task instead of adding new prompts.
- `.github/hooks/*.json` — deterministic automation only (e.g. reminding to sync `documentation/*.md` when `locator_lense/` changes). Use instructions, not hooks, for anything that is guidance rather than an enforceable check.
- `.github/workflows/*.yml` — CI enforcement (tests, lint, CodeQL) that backs the Code Review, Verification, and PR Validation phases with real, automated evidence rather than agent-asserted claims.

# MCP Integration

The workspace configuration (`.vscode/mcp.json`) defines remote GitHub, Jira, and Knowledge Base MCP servers. Do not grant their tools to an agent by default: local `read` and `search` provide the repository context needed for the current SDLC workflow.

Before referencing an MCP tool in agent frontmatter, validate its exact exposed name and the server's authentication flow. Grant each agent only the specific tool it needs, never a server-wide wildcard:

- Knowledge Base tools are for retrieving external standards, policies, or reference documentation.
- Jira tools are for retrieving a user-supplied issue, story, bug, task, or acceptance criteria.
- GitHub tools are for remote repository, pull request, branch, commit, or workflow operations that cannot be satisfied from the workspace.

Document the reason and least-privilege agent mapping in `documentation/architecture.md` before adding any new MCP server or agent-level MCP tool grant.

---

# Quality Goal

Each output should be:

- Complete
- Consistent
- Reviewable
- Testable
- Traceable
- Production-oriented
