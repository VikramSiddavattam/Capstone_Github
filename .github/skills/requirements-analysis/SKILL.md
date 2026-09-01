---
name: requirements-analysis
description: 'Transform business needs, user stories, and feature requests into clear, complete, testable software requirements. Use when eliciting functional/non-functional requirements, classifying constraints and dependencies, resolving ambiguity, or defining measurable acceptance criteria. Reused by the Requirements Agent (authoring) and the Verification Agent (validating delivered acceptance criteria).'
---

# Requirements Analysis Skill

## When to Use

- Converting a user story, business requirement, or feature request into a structured spec.
- Checking whether delivered functionality satisfies the original acceptance criteria (verification pass).

## Procedure

1. **Collect sources**: use supplied attachments as the primary source. When supplied, retrieve the Jira issue by ID and the Confluence page/KB reference with the assigned MCP tools. Record every source identifier used.
2. **Discover**: identify business goals, stakeholders, users, and expected outcomes from the collected sources.
3. **Reconcile sources**: compare material statements across attachments, Jira, and KB. Preserve the attachment's position as primary unless it explicitly identifies another authoritative source. Record conflicts, affected requirements, and needed resolutions; never silently merge contradictory statements.
4. **Classify**: sort findings into Functional Requirements, Non-Functional Requirements, Constraints, and Dependencies.
5. **Gap analysis**: flag ambiguities, incomplete statements, and missing information. Generate clarification questions instead of guessing.
6. **Validate**: verify completeness, consistency, testability, and traceability by linking every requirement to one or more source references.
7. **Define acceptance criteria**: express each requirement as a measurable, pass/fail condition.
8. Record any unresolved question or unstated assumption explicitly rather than inventing scope.

## Outputs

- Source References
- Functional Requirements
- Non-Functional Requirements
- Assumptions
- Constraints
- Dependencies
- Acceptance Criteria
- Identified Gaps and Clarification Questions
- Source Conflicts

## Deliverable

`documentation/requirements.md`
