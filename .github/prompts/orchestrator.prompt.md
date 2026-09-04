---
description: Execute the end-to-end SDLC workflow using the SDLC Orchestrator Agent.
---

# SDLC Orchestration

Use the SDLC Orchestrator Agent to coordinate the complete software development lifecycle for the provided request.

Supported inputs include:

- Jira Story or Defect
- Confluence Page or Knowledge Base Reference
- User Story
- Business Requirement
- Feature Request
- Enhancement Request
- Bug Fix Request
- Source Code Change

The Orchestrator Agent will:

- Coordinate the appropriate SDLC agents.
- Apply repository standards and quality gates.
- Use available documentation, project knowledge, and MCP integrations.
- Generate and maintain required SDLC artifacts.
- Produce implementation, review, verification, and pull-request outputs as required.

Follow all repository guidance defined in:

- `.github/copilot-instructions.md`
- `.github/agents/`
- `.github/skills/`
- `.github/hooks/`

Execute the workflow until all mandatory quality gates are satisfied or blockers are reported.
