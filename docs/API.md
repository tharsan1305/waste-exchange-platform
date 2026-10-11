# REST API Specification (/api/v1)

Base URL: `http://localhost:8000/api/v1`  
All protected routes require standard Bearer token authorization:
```http
Authorization: Bearer <supabase_jwt_access_token>
```

---

## 1. Global JSON Error Response Format
All errors return consistent JSON payloads without exposing server stack traces:
```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "Only verified industries can publish waste listings.",
    "request_id": "req_8492048f-28c0-4382-b7e1-88f6be4e3579",
    "timestamp": "2026-10-11T15:45:00Z"
  }
}
```

---

## 2. API Routers Summary

### 2.1 Auth & Profiles (`/auth`)
- `GET /auth/me`: Returns current user profile, role, and associated industry details.
- `GET /auth/sessions`: Lists active login sessions and device fingerprints.
- `DELETE /auth/sessions/{id}`: Revokes an active session.
- `POST /auth/logout-all`: Revokes all sessions across all devices.

### 2.2 Industries (`/industries`)
- `POST /industries`: Registers an industry profile with address and coordinates.
- `GET /industries/{id}/public`: Retrieves public info, verified badges, and trust score.
- `POST /industries/{id}/documents`: Uploads GST certificate, license, or PCB authorization.
- `PUT /industries/{id}/verify`: (Admin only) Approves, rejects, or suspends an industry.

### 2.3 Listings (`/listings`)
- `GET /listings`: Filterable search by category, waste type, hazardous status, quantity, price, radius, and fulltext query.
- `POST /listings`: Creates a new byproduct listing (Requires approved industry).
- `GET /listings/{id}`: Retrieves full listing specs, quality parameters, and lab reports.
- `GET /listings/passport/{batch_code}`: Public QR waste passport view.
- `PUT /listings/{id}`: Updates listing details.
- `DELETE /listings/{id}`: Archives or removes a listing.

### 2.4 Matching Engine (`/matching`)
- `GET /matching/listings/{id}`: Returns top candidate industries with 0–100 match score breakdown.
- `GET /matching/recommendations`: Returns personalized recommendations for the authenticated industry.

### 2.5 Requests & RFQ (`/requests`, `/rfq`)
- `POST /requests`: Submits a quote/request for a specific listing.
- `GET /requests`: Lists incoming and outgoing requests.
- `PUT /requests/{id}/status`: Accepts or rejects a request (Accepting transitions to a new `deal`).
- `POST /rfq`: Posts a Request for Quote.
- `POST /rfq/{id}/quotes`: Submits a supplier quote.

### 2.6 Deals & Manifests (`/deals`)
- `GET /deals`: Lists active and completed contracts.
- `GET /deals/{id}`: Returns deal details, counterparty contact (if agreed), and status history.
- `PUT /deals/{id}/stage`: Transitions deal stage (`negotiation` $\rightarrow$ `agreed` $\rightarrow$ `payment_confirmed` $\rightarrow$ `pickup_scheduled` $\rightarrow$ `delivered` $\rightarrow$ `completed`).
- `GET /deals/{id}/manifest`: Generates or downloads the cryptographic e-challan PDF.

### 2.7 Geo & Logistics (`/geo`)
- `GET /geo/nearby-industries`: Finds facilities within a given radius.
- `GET /geo/transport-estimate`: Computes distance, drive time, and transport freight in INR based on tonnage.

### 2.8 Pricing Intelligence (`/pricing`)
- `GET /pricing/suggest`: Computes suggested price bands (min, avg, max) from historical completed deals.

### 2.9 Reviews & Trust (`/reviews`)
- `POST /reviews`: Submits a multi-criteria review (1–5 stars) for a completed deal.
- `GET /reviews/industry/{id}`: Lists verified feedback for a company.

### 2.10 Dashboard & Public Stats (`/dashboard`, `/public`)
- `GET /dashboard/industry`: Returns company waste diverted, $\text{CO}_2$ saved, and cost benefits.
- `GET /dashboard/admin`: High-level platform KPIs, verification backlog, and fraud flags.
- `GET /public/stats`: Cached live metrics for landing page counters.
- `GET /network/graph`: Nodes and edges for React Flow industrial symbiosis diagram.
