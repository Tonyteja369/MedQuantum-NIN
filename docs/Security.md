# Security Documentation

## Implemented Controls

- Input validation for ECG uploads and signal IDs
- File size limits and format allowlist
- UUID-based temporary signal identifiers
- Request logging middleware
- Environment-based configuration

## Repository Security Automation

Planned/implemented workflows include:
- CodeQL analysis
- Dependency review for pull requests
- Secret scanning baseline check

## Responsible Disclosure

Refer to root `SECURITY.md` for reporting instructions.

## Secure Deployment Recommendations

- Restrict CORS to trusted frontend domains
- Terminate TLS at ingress/proxy layer
- Avoid exposing backend directly to the internet without auth controls
- Use secret managers (not committed `.env` files) in production
