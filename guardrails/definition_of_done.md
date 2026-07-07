A change is not "done" until all of the following are true:
- Tests pass on the critical path, including at least one failure-mode test (not just the happy path).
- A rollback plan exists and has been stated, not just assumed.
- Monitoring/alerting is in place for the new behavior before it reaches production traffic.
- A short design note or ADR documents the decision and the reasoning behind it, including alternatives considered.
- Any cross-team data contract has been reviewed and acknowledged by the consuming team before launch, not discovered after.
