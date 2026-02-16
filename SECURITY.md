# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in COMB, please report it responsibly.

**Email:** ava@artifactvirtual.com

**Do NOT** open a public GitHub issue for security vulnerabilities.

## What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Response Timeline

- **Acknowledgment:** Within 48 hours
- **Assessment:** Within 1 week
- **Fix:** Depends on severity, but we aim for <2 weeks for critical issues

## Scope

- The `comb` Python package
- Hash chain integrity
- Data corruption or loss scenarios
- Path traversal or injection via user input

## Out of Scope

- Denial of service via large files (known limitation of file-based storage)
- Issues in optional dependencies (click, etc.)
- Social engineering

## Disclosure

We follow coordinated disclosure. We'll credit reporters unless they prefer anonymity.
