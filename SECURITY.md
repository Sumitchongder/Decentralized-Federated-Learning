# Security Policy

## Overview

This repository implements a **decentralized federated learning framework**
with cryptographic verification, secure aggregation, and blockchain integration.

Security is a core design principle, and responsible disclosure is essential.

---

## Supported Versions

Only the **latest version of the main branch** is supported for security fixes.

---

## Reporting a Vulnerability

Please **do not open public GitHub issues** for security vulnerabilities.

Instead, report vulnerabilities via:

- GitHub Security Advisories (preferred)
- Direct private contact with the maintainer

Include the following:

- Description of the vulnerability
- Potential impact and attack surface
- Reproduction steps (if safe)
- Suggested mitigation (optional)

---

## In-Scope Vulnerabilities

- Secure aggregation flaws
- Gossip protocol manipulation
- Model poisoning or replay vulnerabilities
- Signature verification bypass
- Blockchain consensus or ledger tampering
- Client identity spoofing
- Privacy leakage via model updates

---

## Out-of-Scope Issues

- Vulnerabilities caused by user misconfiguration
- Third-party dependency vulnerabilities (unless exploitable here)
- Attacks requiring physical access
- Denial-of-service outside protocol design scope

---

## Responsible Disclosure

We ask reporters to:

- Act in good faith
- Avoid public disclosure before remediation
- Limit testing to proof-of-concept exploitation

---

## Disclaimer

This framework is intended for **research and experimental use**.
It has not undergone formal third-party security audits and should not be
deployed in production environments without additional safeguards,
formal verification, and cryptographic review.

---

Thank you for helping keep decentralized learning secure.
