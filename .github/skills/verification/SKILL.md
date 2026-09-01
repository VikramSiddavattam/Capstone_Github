---
name: verification
description: 'Confirm implemented functionality actually satisfies requirements and acceptance criteria using test execution results and traceable evidence, not assumptions. Use before declaring work complete or preparing a pull request. Reused by the Verification Agent (running the full check) and the PR Agent (citing verified evidence in the PR description).'
---

# Verification Skill

## When to Use

- Confirming a completed implementation is ready to be marked done.
- Gathering test evidence to cite in a pull request description.

## Procedure

1. **Trace requirements**: map each acceptance criterion in `documentation/requirements.md` to the code/tests that satisfy it.
2. **Execute tests**: run the project's automated test suite; never assume tests pass without running them.
3. **Evaluate coverage**: identify acceptance criteria without a corresponding automated test and flag them as a gap.
4. **Check documentation sync**: confirm `documentation/*.md` reflects the current implementation.
5. **Check review closure**: confirm findings from `documentation/code-review.md` / `documentation/design-review.md` are resolved or explicitly accepted as known limitations.
6. Report results as pass/fail per requirement with links to evidence (test names, files); do not report a global "pass" without itemized evidence.

## Outputs

- Requirement-to-test traceability table
- Test execution results
- Coverage gaps
- Outstanding known limitations

## Deliverable

`documentation/verification-report.md`
