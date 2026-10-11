# Security Architecture & Threat Model (SECURITY.md)

This document outlines the security controls, threat mitigations, and compliance measures engineered into the **Waste Exchange Platform**, aligned with OWASP Top 10 standards.

---

## 1. OWASP Top 10 Mitigation Matrix

| # | OWASP Risk | Platform Vulnerability Vectors | Applied Engineering Mitigation |
|---|------------|--------------------------------|--------------------------------|
| **A01:2021** | **Broken Access Control** | Unauthorized listing edits, viewing competitor deals, reading private KYC documents. | • Postgres RLS policies active on all 25 tables.<br>• FastAPI dependency `require_approved_industry` and `require_role('admin')`.<br>• Storage bucket access restricted to tenant UUID folder structure. |
| **A02:2021** | **Cryptographic Failures** | Plaintext document storage, token interception, weak password hashing. | • Passwords managed via Supabase Auth (Argon2 / bcrypt).<br>• HTTPS-only communication with strict HSTS.<br>• Sensitive KYC documents encrypted via AES-256-GCM envelope before storage. |
| **A03:2021** | **Injection** | SQL Injection, XSS in chat negotiation, NoSQL injection in JSONB filters. | • Parameterized SQL via Supabase PostgREST & SQLAlchemy.<br>• Strict Pydantic v2 schemas reject unknown fields.<br>• React DOM auto-escaping (strict ban on `dangerouslySetInnerHTML`). |
| **A04:2021** | **Insecure Design** | Circumventing platform fee via contact leakage; counterfeit waste claims. | • Phone/email regex masking in chat until deal status reaches `agreed`.<br>• Mandatory admin verification of GSTIN & PCB authorization.<br>• Non-repudiable PDF e-challan with SHA-256 fingerprint. |
| **A05:2021** | **Security Misconfiguration** | Exposed API docs in production, permissive CORS, default cloud credentials. | • FastAPI OpenAPI `/docs` enabled only when `ENVIRONMENT=development`.<br>• Strict CORS origin whitelist.<br>• Helmet security headers (CSP, X-Frame-Options: DENY, X-Content-Type-Options: nosniff). |
| **A06:2021** | **Vulnerable & Outdated Components** | Known CVEs in Python or Node packages. | • GitHub Dependabot & CI security vulnerability scanning.<br>• Strict version pinning in `requirements.txt` and `package.json`. |
| **A07:2021** | **Identification & Authentication Failures** | Brute force login, session hijacking, lack of MFA for admin. | • Native TOTP 2FA enrollment for administrative users.<br>• SlowAPI rate limiting (5 attempts/minute on auth routes).<br>• Auto-lockout and anomaly notification on unknown IP/User-Agent. |
| **A08:2021** | **Software & Data Integrity Failures** | Tampering with uploaded lab reports or transport manifests. | • SHA-256 cryptographic hash calculated on upload and stored in DB.<br>• Dedicated `/integrity-check` endpoint verifies file hash against stored fingerprint.<br>• Manifest PDFs contain QR-embedded cryptographic hash. |
| **A09:2021** | **Security Logging & Monitoring Failures** | Unaudited privilege escalation, untracked dispute tampering. | • Immutable `audit_logs` table (REVOKE UPDATE/DELETE).<br>• All write endpoints log user ID, role, action, client IP, and payload snapshot.<br>• Background fraud scanner flags document hash reuse across accounts. |
| **A10:2021** | **Server-Side Request Forgery (SSRF)** | Exploitation of routing/distance calculation requests. | • OSRM routing endpoint URL is strictly controlled via environment config.<br>• Geolocation queries validate latitude (-90 to 90) and longitude (-180 to 180). |

---

## 2. Threat Modeling & Attack Scenarios

### Scenario A: Unverified Industry Attempts to List Hazardous Waste
- **Threat:** Malicious actor signs up with a fake name to dump toxic chemical sludge.
- **Defense Mechanism:**
  1. The industry row starts in `verification_status = 'pending'`.
  2. The Postgres RLS policy `Only approved industries can insert listings` blocks `INSERT` attempts at the database level.
  3. The FastAPI endpoint enforces `require_approved_industry`, throwing HTTP 403 Forbidden.
  4. If the listing is marked `is_hazardous = true`, the system requires a valid `pcb_authorization_no` and verified lab test certificate.

### Scenario B: Disintermediation Attack (Bypassing Platform in Negotiation)
- **Threat:** Buyer and seller exchange phone numbers in chat during initial contact to deal offline.
- **Defense Mechanism:**
  1. FastAPI chat router applies regular expressions to detect and redact 10-digit Indian mobile numbers, emails, and WhatsApp invitation links.
  2. The seller's contact details view returns masked strings (`+91 98*****56`) until the deal stage is formally transitioned to `agreed`.

### Scenario C: Reused Document Fraud (Sybil Attack)
- **Threat:** Fraudulent user uploads the same GST certificate or PCB license across multiple fake accounts.
- **Defense Mechanism:**
  1. Upon file upload, the backend computes the SHA-256 digest.
  2. The fraud service queries `industry_documents` for identical hashes belonging to other `industry_id`s.
  3. A `fraud_flags` entry is created with severity `critical`, instantly alerting platform administrators and locking the account.
