-- =====================================================================
-- Migration 02: Core Relational Schema, Indexes, Views
-- Platform: Supabase PostgreSQL
-- =====================================================================

-- 1. Profiles Table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    phone TEXT,
    role user_role NOT NULL DEFAULT 'industry_admin',
    industry_id UUID,
    preferred_language TEXT NOT NULL DEFAULT 'en',
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 2. Industries Table
CREATE TABLE IF NOT EXISTS public.industries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    gst_number TEXT NOT NULL UNIQUE,
    license_number TEXT,
    industry_type TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'Tamil Nadu',
    pincode TEXT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    contact_email TEXT NOT NULL,
    contact_phone TEXT NOT NULL,
    verification_status verification_status NOT NULL DEFAULT 'pending',
    verified_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    rejection_reason TEXT,
    trust_score NUMERIC(3, 2) NOT NULL DEFAULT 5.00,
    pcb_authorization_no TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Idempotent Foreign Key for profiles -> industries
DO $$ BEGIN
    ALTER TABLE public.profiles
        ADD CONSTRAINT fk_profiles_industry
        FOREIGN KEY (industry_id) REFERENCES public.industries(id) ON DELETE SET NULL;
EXCEPTION 
    WHEN duplicate_object THEN NULL;
END $$;

-- 3. Industry Documents (Stored in AWS S3 with SHA-256 integrity)
CREATE TABLE IF NOT EXISTS public.industry_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    doc_type industry_doc_type NOT NULL,
    s3_bucket TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    storage_path TEXT NOT NULL, -- s3://bucket/key
    sha256_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    uploaded_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);
CREATE INDEX IF NOT EXISTS idx_industry_docs_hash ON public.industry_documents(sha256_hash);
CREATE INDEX IF NOT EXISTS idx_industry_docs_industry ON public.industry_documents(industry_id);

-- 4. Waste Categories
CREATE TABLE IF NOT EXISTS public.waste_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 5. Waste Types (e.g. Bagasse, Fly Ash, Steel Slag)
CREATE TABLE IF NOT EXISTS public.waste_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES public.waste_categories(id) ON DELETE RESTRICT,
    name TEXT NOT NULL UNIQUE,
    is_hazardous_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 6. Waste Usage Rules (Rule-based matching matrix)
CREATE TABLE IF NOT EXISTS public.waste_usage_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    waste_type_id UUID NOT NULL REFERENCES public.waste_types(id) ON DELETE CASCADE,
    industry_type TEXT NOT NULL,
    use_case TEXT NOT NULL,
    priority INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 7. Waste Listings
CREATE TABLE IF NOT EXISTS public.waste_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    waste_type_id UUID NOT NULL REFERENCES public.waste_types(id) ON DELETE RESTRICT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    quantity NUMERIC(14, 2) NOT NULL,
    unit waste_unit NOT NULL DEFAULT 'ton',
    price_per_unit NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    currency TEXT NOT NULL DEFAULT 'INR',
    is_hazardous BOOLEAN NOT NULL DEFAULT FALSE,
    hazard_class TEXT,
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    recurrence recurrence_type,
    available_from TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    expires_at TIMESTAMPTZ NOT NULL,
    status listing_status NOT NULL DEFAULT 'available',
    batch_code TEXT NOT NULL UNIQUE,
    qr_path TEXT,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    quality_params JSONB NOT NULL DEFAULT '{}'::jsonb,
    images TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);
CREATE INDEX IF NOT EXISTS idx_listings_status_waste_type ON public.waste_listings(status, waste_type_id);
CREATE INDEX IF NOT EXISTS idx_listings_geo ON public.waste_listings(lat, lng);

-- 8. Listing Documents (Lab Test Reports stored in AWS S3)
CREATE TABLE IF NOT EXISTS public.listing_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES public.waste_listings(id) ON DELETE CASCADE,
    doc_type listing_doc_type NOT NULL DEFAULT 'lab_report',
    s3_bucket TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    sha256_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 9. Direct Purchase Requests
CREATE TABLE IF NOT EXISTS public.requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES public.waste_listings(id) ON DELETE CASCADE,
    buyer_industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    quantity NUMERIC(14, 2) NOT NULL,
    offered_price NUMERIC(12, 2) NOT NULL,
    message TEXT,
    status request_status NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 10. RFQ Requests
CREATE TABLE IF NOT EXISTS public.rfq_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buyer_industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    waste_type_id UUID NOT NULL REFERENCES public.waste_types(id) ON DELETE RESTRICT,
    quantity NUMERIC(14, 2) NOT NULL,
    unit waste_unit NOT NULL DEFAULT 'ton',
    max_price NUMERIC(12, 2),
    location_radius_km NUMERIC(8, 2) NOT NULL DEFAULT 100.0,
    needed_by DATE,
    description TEXT,
    status rfq_status NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 11. RFQ Quotes
CREATE TABLE IF NOT EXISTS public.rfq_quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id UUID NOT NULL REFERENCES public.rfq_requests(id) ON DELETE CASCADE,
    seller_industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    listing_id UUID REFERENCES public.waste_listings(id) ON DELETE SET NULL,
    price_per_unit NUMERIC(12, 2) NOT NULL,
    quantity NUMERIC(14, 2) NOT NULL,
    note TEXT,
    status rfq_quote_status NOT NULL DEFAULT 'submitted',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 12. Saved Searches & Alerts
CREATE TABLE IF NOT EXISTS public.saved_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    filters JSONB NOT NULL DEFAULT '{}'::jsonb,
    notify_email BOOLEAN NOT NULL DEFAULT TRUE,
    notify_sms BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 13. Deals (Contract Lifecycle & ESG Impact)
CREATE TABLE IF NOT EXISTS public.deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES public.waste_listings(id) ON DELETE SET NULL,
    seller_industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE RESTRICT,
    buyer_industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE RESTRICT,
    quantity NUMERIC(14, 2) NOT NULL,
    agreed_price_per_unit NUMERIC(12, 2) NOT NULL,
    total_amount NUMERIC(14, 2) NOT NULL,
    stage deal_stage NOT NULL DEFAULT 'negotiation',
    payment_status payment_status NOT NULL DEFAULT 'pending',
    vehicle_number TEXT,
    transporter_name TEXT,
    transporter_pcb_auth_no TEXT,
    pickup_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    co2_saved_kg NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    landfill_diverted_kg NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    money_saved NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);
CREATE INDEX IF NOT EXISTS idx_deals_seller ON public.deals(seller_industry_id);
CREATE INDEX IF NOT EXISTS idx_deals_buyer ON public.deals(buyer_industry_id);
CREATE INDEX IF NOT EXISTS idx_deals_stage ON public.deals(stage);

-- 14. Deal Stage History
CREATE TABLE IF NOT EXISTS public.deal_stage_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES public.deals(id) ON DELETE CASCADE,
    from_stage deal_stage,
    to_stage deal_stage NOT NULL,
    changed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 15. Manifests (E-Challan PDFs stored in AWS S3)
CREATE TABLE IF NOT EXISTS public.manifests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL UNIQUE REFERENCES public.deals(id) ON DELETE CASCADE,
    s3_bucket TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    pdf_path TEXT NOT NULL,
    sha256_hash TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 16. Messages (Negotiation & Chat)
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
    request_id UUID REFERENCES public.requests(id) ON DELETE CASCADE,
    sender_industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    sender_user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    body TEXT NOT NULL,
    quote_price NUMERIC(12, 2),
    quote_quantity NUMERIC(14, 2),
    is_quote BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);
CREATE INDEX IF NOT EXISTS idx_messages_deal ON public.messages(deal_id, created_at);
CREATE INDEX IF NOT EXISTS idx_messages_request ON public.messages(request_id, created_at);

-- 17. Notifications
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    industry_id UUID REFERENCES public.industries(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    channel notification_channel NOT NULL DEFAULT 'in_app',
    status notification_status NOT NULL DEFAULT 'queued',
    read_at TIMESTAMPTZ,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON public.notifications(user_id, read_at);

-- 18. Reviews & Ratings
CREATE TABLE IF NOT EXISTS public.reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES public.deals(id) ON DELETE CASCADE,
    reviewer_industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    reviewee_industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    quality INT NOT NULL CHECK (quality BETWEEN 1 AND 5),
    quantity INT NOT NULL CHECK (quantity BETWEEN 1 AND 5),
    on_time_delivery INT NOT NULL CHECK (on_time_delivery BETWEEN 1 AND 5),
    communication INT NOT NULL CHECK (communication BETWEEN 1 AND 5),
    comment TEXT,
    sentiment sentiment_label NOT NULL DEFAULT 'positive',
    sentiment_score NUMERIC(3, 2) NOT NULL DEFAULT 0.85,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    CONSTRAINT uq_deal_reviewer UNIQUE (deal_id, reviewer_industry_id)
);

-- 19. Badges & Industry Badges
CREATE TABLE IF NOT EXISTS public.badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public.industry_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES public.badges(id) ON DELETE CASCADE,
    awarded_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    CONSTRAINT uq_industry_badge UNIQUE (industry_id, badge_id)
);

-- 20. Complaints
CREATE TABLE IF NOT EXISTS public.complaints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID REFERENCES public.deals(id) ON DELETE SET NULL,
    listing_id UUID REFERENCES public.waste_listings(id) ON DELETE SET NULL,
    raised_by_industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    against_industry_id UUID NOT NULL REFERENCES public.industries(id) ON DELETE CASCADE,
    type complaint_type NOT NULL,
    description TEXT NOT NULL,
    evidence_paths TEXT[] NOT NULL DEFAULT '{}',
    status complaint_status NOT NULL DEFAULT 'open',
    resolution_note TEXT,
    resolved_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 21. Platform Feedback
CREATE TABLE IF NOT EXISTS public.platform_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    type feedback_type NOT NULL DEFAULT 'suggestion',
    message TEXT NOT NULL,
    sentiment sentiment_label NOT NULL DEFAULT 'neutral',
    status TEXT NOT NULL DEFAULT 'new',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 22. Emission Factors
CREATE TABLE IF NOT EXISTS public.emission_factors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    waste_type_id UUID NOT NULL UNIQUE REFERENCES public.waste_types(id) ON DELETE CASCADE,
    kg_co2e_avoided_per_ton NUMERIC(10, 2) NOT NULL,
    landfill_factor NUMERIC(4, 2) NOT NULL DEFAULT 1.0,
    source_note TEXT NOT NULL DEFAULT 'Illustrative placeholder value. Subject to PCB validation.',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 23. Login Sessions
CREATE TABLE IF NOT EXISTS public.login_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    ip TEXT NOT NULL,
    user_agent TEXT,
    device_fingerprint TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    revoked_at TIMESTAMPTZ
);

-- 24. Audit Logs (Append-Only)
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    actor_role TEXT,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT,
    ip TEXT,
    user_agent TEXT,
    before JSONB,
    after JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);
CREATE INDEX IF NOT EXISTS idx_audit_time ON public.audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON public.audit_logs(actor_user_id);

-- 25. Fraud Flags
CREATE TABLE IF NOT EXISTS public.fraud_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    rule_code TEXT NOT NULL,
    severity fraud_severity NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    status fraud_status NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- =====================================================================
-- HELPER VIEWS & AGGREGATIONS
-- =====================================================================

CREATE OR REPLACE VIEW public.industry_impact_summary AS
SELECT 
    ind.id AS industry_id,
    ind.name AS industry_name,
    COALESCE(SUM(CASE WHEN d.seller_industry_id = ind.id THEN d.quantity ELSE 0 END), 0) AS total_waste_supplied_tonnes,
    COALESCE(SUM(CASE WHEN d.buyer_industry_id = ind.id THEN d.quantity ELSE 0 END), 0) AS total_waste_diverted_tonnes,
    COALESCE(SUM(d.co2_saved_kg), 0) / 1000.0 AS total_co2_saved_tonnes,
    COALESCE(SUM(d.landfill_diverted_kg), 0) / 1000.0 AS total_landfill_saved_tonnes,
    COALESCE(SUM(d.money_saved), 0) AS total_money_saved_inr
FROM public.industries ind
LEFT JOIN public.deals d ON (ind.id = d.seller_industry_id OR ind.id = d.buyer_industry_id) AND d.stage = 'completed'
GROUP BY ind.id, ind.name;

CREATE OR REPLACE VIEW public.monthly_waste_history AS
SELECT 
    date_trunc('month', d.created_at) AS month,
    wt.name AS waste_type_name,
    COUNT(d.id) AS total_deals,
    SUM(d.quantity) AS total_tonnes,
    SUM(d.co2_saved_kg) AS total_co2_kg,
    SUM(d.total_amount) AS total_volume_inr
FROM public.deals d
JOIN public.waste_listings wl ON d.listing_id = wl.id
JOIN public.waste_types wt ON wl.waste_type_id = wt.id
WHERE d.stage = 'completed'
GROUP BY date_trunc('month', d.created_at), wt.name
ORDER BY month DESC;

CREATE OR REPLACE VIEW public.platform_stats_public AS
SELECT 
    (SELECT COUNT(*) FROM public.industries WHERE verification_status = 'approved') AS verified_industries_count,
    (SELECT COUNT(*) FROM public.waste_listings WHERE status = 'available') AS active_listings_count,
    (SELECT COALESCE(SUM(landfill_diverted_kg) / 1000.0, 0) FROM public.deals WHERE stage = 'completed') AS total_tonnes_diverted,
    (SELECT COALESCE(SUM(co2_saved_kg) / 1000.0, 0) FROM public.deals WHERE stage = 'completed') AS total_co2_tonnes_mitigated,
    (SELECT COALESCE(SUM(total_amount), 0) FROM public.deals WHERE stage = 'completed') AS total_economic_volume_inr;
