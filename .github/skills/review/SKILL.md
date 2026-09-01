---
name: review
description: 'Objective, evidence-based review methodology with severity classification (Critical/High/Medium/Low/Recommendation). Use when reviewing source code or architectural/design artifacts against requirements and standards. Reused by the Code Review Agent (source code) and the Design Review Agent (architecture proposals).'
---

# Review Skill

## When to Use

- Reviewing implemented source code before merge.
- Reviewing an architecture or design proposal before implementation planning begins.

## Procedure

1. **Establish baseline**: read the relevant requirement(s) and, for code reviews, the architecture the change should conform to.
2. **Evaluate systematically** against the applicable dimensions:
   - Correctness / requirements coverage
   - Maintainability and readability
   - Security (input validation, secrets handling, least privilege)
   - Error handling
   - Test coverage (code review) or requirements traceability (design review)
   - Performance and scalability concerns
   - Dependency safety
   - Duplication / unnecessary complexity
3. **Classify every finding** with a severity: `Critical`, `High`, `Medium`, `Low`, `Recommendation`.
4. **Be evidence-based**: cite the specific file/section and explain the concrete impact, not a stylistic preference.
5. **Recommend, don't rewrite**: propose the fix; only edit code directly when explicitly asked.
6. Summarize whether the artifact is approved, approved-with-comments, or blocked, and list required follow-ups.

## Outputs

- Findings list grouped by severity
- Overall verdict (approved / approved-with-comments / blocked)
- Follow-up actions

## Deliverable

`documentation/code-review.md` or `documentation/design-review.md`
