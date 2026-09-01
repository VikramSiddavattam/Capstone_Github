---
name: architecture-design
description: 'Transform approved requirements into a scalable, maintainable, implementable solution architecture: component decomposition, technology selection, data flow, and quality-attribute trade-offs. Use when designing or reviewing system architecture. Reused by the Architecture Agent (authoring) and the Design Review Agent (evaluating the proposal against requirements and quality attributes).'
---

# Architecture Design Skill

## When to Use

- Producing a new or updated architecture from `documentation/requirements.md`.
- Reviewing an existing architecture proposal for gaps, risks, or unnecessary complexity.

## Procedure

1. **Requirement analysis**: read functional and non-functional requirements, constraints, and dependencies.
2. **System decomposition**: identify major capabilities, define system boundaries, components, and their responsibilities.
3. **Design decisions**: select architectural patterns, technology stack, integration and communication approaches — only where justified by requirements. Do not introduce technology without a documented reason.
4. **Quality attribute evaluation**: assess scalability, performance, security, reliability, maintainability, and extensibility.
5. **Risk assessment**: document architectural risks, assumptions, and mitigation strategies.
6. **Traceability check**: confirm every requirement maps to at least one architectural component, and every component traces back to a requirement.

## Outputs

- High-Level Architecture
- Component Architecture
- Data Flow
- Technology Recommendations
- Architectural Decisions and Trade-offs
- Risks and Mitigations

## Deliverable

`documentation/architecture.md` (authoring) or `documentation/design-review.md` (review findings against this checklist).
