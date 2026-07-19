# Security Policy

## Supported Versions

Security fixes are provided on a best-effort basis for the latest default branch.

## Reporting a Vulnerability

Please report vulnerabilities privately:

1. Open a private security advisory in GitHub (preferred), or
2. Contact repository maintainers via the repository issue tracker with a request for private handling.

Include:
- Vulnerability description
- Affected components/files
- Reproduction steps
- Potential impact
- Suggested mitigation (if available)

## Response Process

- Acknowledgement target: within 5 business days
- Triage: validate severity and impact
- Remediation: patch and test
- Disclosure: coordinated disclosure after a fix is available

## Security Practices in this Repository

- Dependency pinning in `backend/requirements.txt`
- Input and signal validation in backend ingestion utilities
- UUID validation for temporary signal identifiers
- CI security workflows (CodeQL, dependency review, secret scanning)

## Scope Note

This software is not a certified medical device. Clinical users must independently validate all outputs before patient care decisions.
