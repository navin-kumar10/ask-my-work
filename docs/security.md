# Security

Ask My Work is intentionally read-only in v0.1.

### Allowed
- Read approved text submitted through the API
- Create user-authored notes
- Search stored knowledge
- Generate answers from retrieved evidence

### Explicitly blocked
- Shell execution
- File modification/deletion
- Software installation
- Network scanning
- Autonomous remediation
- Secret storage

Secrets are redacted before persistence. Organization-wide knowledge sharing is a future opt-in/approval feature, not a default behavior.
