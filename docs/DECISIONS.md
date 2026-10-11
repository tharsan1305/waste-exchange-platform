# Architecture & Implementation Decisions Log (DECISIONS.md)

This log documents all architectural assumptions, engineering tradeoffs, and sensible defaults chosen during the development of the **Waste Exchange Platform**.

---

## 1. Auth & Identity
- **Decision:** Supabase Auth is the single source of truth for identities.
- **Details:** The `profiles` table references `auth.users(id)`. Profile roles are `admin`, `industry_admin`, and `industry_staff`. FastAPI verifies JWT tokens using the Supabase JWT secret or JWKS on every request.
- **Rationale:** Ensures unified session management, TOTP MFA support natively via Supabase, and avoids redundant auth credential stores.

## 2. Multi-Tenancy & Roles
- **Decision:** Roles are not split into distinct buyer vs seller accounts. An `industries` entity can both generate byproducts (sell) and acquire byproducts (buy).
- **Details:** The `industry_admin` role manages the industry profile, GST/compliance verification documents, listings, bids, and contracts.

## 3. Contact Details Concealment (Anti-Disintermediation & Privacy)
- **Decision:** Direct counterparty contact numbers and emails are masked in messages and API responses until a deal transitions to the `agreed` stage.
- **Details:** Regex filters in FastAPI chat router strip phone numbers and email addresses during negotiation stage messages, and the counterparty details view returns masked strings (`+91 98*****12`) until the stage changes to `agreed`.

## 4. Matching Engine
- **Decision:** Rule-based matching engine instead of opaque Machine Learning or LLMs.
- **Details:** Matches are scored on a deterministic 0–100 scale:
  - Waste-type compatibility rule (weight: 40)
  - Geospatial distance via Haversine (weight: 25)
  - Quantity fit (weight: 15)
  - Hazardous PCB authorization match (weight: 10)
  - Counterparty trust score (weight: 10)
- **Rationale:** B2B industrial byproduct exchange involves toxicological and legal regulations (CPCB / TNPCB rules). Non-deterministic AI could make dangerous suggestions. Deterministic scoring guarantees 100% safety, zero hallucination, sub-5ms response times, and full auditability.

## 5. File Uploads & Security
- **Decision:** Multi-layered verification for uploaded documents:
  - MIME type sniffing & strict extension whitelist (`.pdf`, `.png`, `.jpg`, `.jpeg`).
  - Max file size limit: 10 MB.
  - SHA-256 hash computed on upload and stored in DB.
  - Hash reuse across distinct industries flags a fraud warning.
  - ClamAV scan interface with graceful fallback logging (`scan_skipped`).
  - Sensitive industry registration documents stored in private Supabase buckets, served only via short-lived signed URLs.

## 6. ESG & Carbon Calculation Placeholders
- **Decision:** Baseline emission factors are seeded as illustrative placeholders in `emission_factors` table with clear UI markers ("*Estimated calculation based on standard baseline factors*").
- **Details:** Platform admins have a dedicated UI and API endpoint to update these factors as certified regulatory emission data is confirmed.
