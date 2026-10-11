-- =====================================================================
-- Migration 03: Row Level Security (RLS) & Multi-Tenant Policies (Idempotent)
-- Platform: Supabase PostgreSQL
-- =====================================================================

-- Helper Security Functions
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.profiles
        WHERE id = auth.uid() AND role = 'admin'
    );
$$;

CREATE OR REPLACE FUNCTION public.current_user_industry_id()
RETURNS UUID
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
STABLE
AS $$
    SELECT industry_id FROM public.profiles
    WHERE id = auth.uid();
$$;

CREATE OR REPLACE FUNCTION public.is_approved_industry()
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.profiles p
        JOIN public.industries i ON p.industry_id = i.id
        WHERE p.id = auth.uid() AND i.verification_status = 'approved'
    );
$$;

-- ---------------------------------------------------------------------
-- 1. Enable RLS on All Tables
-- ---------------------------------------------------------------------
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.industries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.industry_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.waste_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.waste_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.waste_usage_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.waste_listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.listing_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rfq_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rfq_quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_searches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deal_stage_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.manifests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.badges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.industry_badges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.complaints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.platform_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.emission_factors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.login_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fraud_flags ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------
-- 2. Profiles Policies
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view their own profile or admin can view all" ON public.profiles;
CREATE POLICY "Users can view their own profile or admin can view all"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id OR public.is_admin());

DROP POLICY IF EXISTS "Users can update their own profile" ON public.profiles;
CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id OR public.is_admin());

DROP POLICY IF EXISTS "Users can insert their own profile" ON public.profiles;
CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ---------------------------------------------------------------------
-- 3. Industries Policies
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Public read of approved industries or own industry" ON public.industries;
CREATE POLICY "Public read of approved industries or own industry"
    ON public.industries FOR SELECT
    TO authenticated
    USING (
        verification_status = 'approved' 
        OR id = public.current_user_industry_id() 
        OR public.is_admin()
    );

DROP POLICY IF EXISTS "Industry admins can update their own industry" ON public.industries;
CREATE POLICY "Industry admins can update their own industry"
    ON public.industries FOR UPDATE
    TO authenticated
    USING (id = public.current_user_industry_id() OR public.is_admin());

DROP POLICY IF EXISTS "Authenticated users can register an industry" ON public.industries;
CREATE POLICY "Authenticated users can register an industry"
    ON public.industries FOR INSERT
    TO authenticated
    WITH CHECK (TRUE);

-- ---------------------------------------------------------------------
-- 4. Industry Documents Policies
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Industries can view own documents or admin" ON public.industry_documents;
CREATE POLICY "Industries can view own documents or admin"
    ON public.industry_documents FOR SELECT
    TO authenticated
    USING (industry_id = public.current_user_industry_id() OR public.is_admin());

DROP POLICY IF EXISTS "Industries can upload own documents" ON public.industry_documents;
CREATE POLICY "Industries can upload own documents"
    ON public.industry_documents FOR INSERT
    TO authenticated
    WITH CHECK (industry_id = public.current_user_industry_id() OR public.is_admin());

-- ---------------------------------------------------------------------
-- 5. Waste Taxonomy & Rules Policies
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Authenticated users can read categories" ON public.waste_categories;
CREATE POLICY "Authenticated users can read categories"
    ON public.waste_categories FOR SELECT TO authenticated USING (TRUE);

DROP POLICY IF EXISTS "Admin can modify categories" ON public.waste_categories;
CREATE POLICY "Admin can modify categories"
    ON public.waste_categories FOR ALL TO authenticated USING (public.is_admin());

DROP POLICY IF EXISTS "Authenticated users can read waste types" ON public.waste_types;
CREATE POLICY "Authenticated users can read waste types"
    ON public.waste_types FOR SELECT TO authenticated USING (TRUE);

DROP POLICY IF EXISTS "Admin can modify waste types" ON public.waste_types;
CREATE POLICY "Admin can modify waste types"
    ON public.waste_types FOR ALL TO authenticated USING (public.is_admin());

DROP POLICY IF EXISTS "Authenticated users can read usage rules" ON public.waste_usage_rules;
CREATE POLICY "Authenticated users can read usage rules"
    ON public.waste_usage_rules FOR SELECT TO authenticated USING (TRUE);

DROP POLICY IF EXISTS "Admin can modify usage rules" ON public.waste_usage_rules;
CREATE POLICY "Admin can modify usage rules"
    ON public.waste_usage_rules FOR ALL TO authenticated USING (public.is_admin());

-- ---------------------------------------------------------------------
-- 6. Waste Listings & Documents
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Anyone can view available listings of approved industries or own listings" ON public.waste_listings;
CREATE POLICY "Anyone can view available listings of approved industries or own listings"
    ON public.waste_listings FOR SELECT
    TO authenticated
    USING (
        (status = 'available' AND EXISTS (
            SELECT 1 FROM public.industries i 
            WHERE i.id = waste_listings.industry_id AND i.verification_status = 'approved'
        ))
        OR industry_id = public.current_user_industry_id()
        OR public.is_admin()
    );

DROP POLICY IF EXISTS "Only approved industries can insert listings" ON public.waste_listings;
CREATE POLICY "Only approved industries can insert listings"
    ON public.waste_listings FOR INSERT
    TO authenticated
    WITH CHECK (
        industry_id = public.current_user_industry_id() 
        AND public.is_approved_industry()
    );

DROP POLICY IF EXISTS "Listing owner can update own listings" ON public.waste_listings;
CREATE POLICY "Listing owner can update own listings"
    ON public.waste_listings FOR UPDATE
    TO authenticated
    USING (industry_id = public.current_user_industry_id() OR public.is_admin());

DROP POLICY IF EXISTS "Read listing documents" ON public.listing_documents;
CREATE POLICY "Read listing documents"
    ON public.listing_documents FOR SELECT
    TO authenticated
    USING (TRUE);

DROP POLICY IF EXISTS "Insert listing documents for own listing" ON public.listing_documents;
CREATE POLICY "Insert listing documents for own listing"
    ON public.listing_documents FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.waste_listings wl
            WHERE wl.id = listing_id AND wl.industry_id = public.current_user_industry_id()
        )
        OR public.is_admin()
    );

-- ---------------------------------------------------------------------
-- 7. Requests and RFQs
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Parties or admin can read requests" ON public.requests;
CREATE POLICY "Parties or admin can read requests"
    ON public.requests FOR SELECT
    TO authenticated
    USING (
        buyer_industry_id = public.current_user_industry_id()
        OR EXISTS (
            SELECT 1 FROM public.waste_listings wl 
            WHERE wl.id = requests.listing_id AND wl.industry_id = public.current_user_industry_id()
        )
        OR public.is_admin()
    );

DROP POLICY IF EXISTS "Approved buyers can insert requests" ON public.requests;
CREATE POLICY "Approved buyers can insert requests"
    ON public.requests FOR INSERT
    TO authenticated
    WITH CHECK (
        buyer_industry_id = public.current_user_industry_id() 
        AND public.is_approved_industry()
    );

DROP POLICY IF EXISTS "Parties can update requests" ON public.requests;
CREATE POLICY "Parties can update requests"
    ON public.requests FOR UPDATE
    TO authenticated
    USING (
        buyer_industry_id = public.current_user_industry_id()
        OR EXISTS (
            SELECT 1 FROM public.waste_listings wl 
            WHERE wl.id = requests.listing_id AND wl.industry_id = public.current_user_industry_id()
        )
        OR public.is_admin()
    );

-- ---------------------------------------------------------------------
-- 8. Deals, History & Manifests
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Deal participants or admin can read deals" ON public.deals;
CREATE POLICY "Deal participants or admin can read deals"
    ON public.deals FOR SELECT
    TO authenticated
    USING (
        seller_industry_id = public.current_user_industry_id()
        OR buyer_industry_id = public.current_user_industry_id()
        OR public.is_admin()
    );

DROP POLICY IF EXISTS "Deal participants or admin can update deals" ON public.deals;
CREATE POLICY "Deal participants or admin can update deals"
    ON public.deals FOR UPDATE
    TO authenticated
    USING (
        seller_industry_id = public.current_user_industry_id()
        OR buyer_industry_id = public.current_user_industry_id()
        OR public.is_admin()
    );

DROP POLICY IF EXISTS "Deal participants or admin can read deal stage history" ON public.deal_stage_history;
CREATE POLICY "Deal participants or admin can read deal stage history"
    ON public.deal_stage_history FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.deals d
            WHERE d.id = deal_stage_history.deal_id
            AND (d.seller_industry_id = public.current_user_industry_id() 
                 OR d.buyer_industry_id = public.current_user_industry_id())
        )
        OR public.is_admin()
    );

DROP POLICY IF EXISTS "Deal participants or admin can view manifests" ON public.manifests;
CREATE POLICY "Deal participants or admin can view manifests"
    ON public.manifests FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.deals d
            WHERE d.id = manifests.deal_id
            AND (d.seller_industry_id = public.current_user_industry_id() 
                 OR d.buyer_industry_id = public.current_user_industry_id())
        )
        OR public.is_admin()
    );

-- ---------------------------------------------------------------------
-- 9. Messages
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Deal or request participants can view messages" ON public.messages;
CREATE POLICY "Deal or request participants can view messages"
    ON public.messages FOR SELECT
    TO authenticated
    USING (
        (deal_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM public.deals d
            WHERE d.id = messages.deal_id
            AND (d.seller_industry_id = public.current_user_industry_id() 
                 OR d.buyer_industry_id = public.current_user_industry_id())
        ))
        OR (request_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM public.requests r
            JOIN public.waste_listings wl ON r.listing_id = wl.id
            WHERE r.id = messages.request_id
            AND (r.buyer_industry_id = public.current_user_industry_id() 
                 OR wl.industry_id = public.current_user_industry_id())
        ))
        OR public.is_admin()
    );

DROP POLICY IF EXISTS "Deal or request participants can insert messages" ON public.messages;
CREATE POLICY "Deal or request participants can insert messages"
    ON public.messages FOR INSERT
    TO authenticated
    WITH CHECK (sender_industry_id = public.current_user_industry_id());

-- ---------------------------------------------------------------------
-- 10. Reviews & Trust
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Everyone can read reviews" ON public.reviews;
CREATE POLICY "Everyone can read reviews"
    ON public.reviews FOR SELECT
    TO authenticated
    USING (TRUE);

DROP POLICY IF EXISTS "Completed deal participants can insert review" ON public.reviews;
CREATE POLICY "Completed deal participants can insert review"
    ON public.reviews FOR INSERT
    TO authenticated
    WITH CHECK (
        reviewer_industry_id = public.current_user_industry_id()
        AND EXISTS (
            SELECT 1 FROM public.deals d
            WHERE d.id = reviews.deal_id 
              AND d.stage = 'completed'
              AND (d.seller_industry_id = public.current_user_industry_id() 
                   OR d.buyer_industry_id = public.current_user_industry_id())
        )
    );

-- ---------------------------------------------------------------------
-- 11. Complaints & Platform Feedback
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Complainant or accused or admin can view complaint" ON public.complaints;
CREATE POLICY "Complainant or accused or admin can view complaint"
    ON public.complaints FOR SELECT
    TO authenticated
    USING (
        raised_by_industry_id = public.current_user_industry_id()
        OR against_industry_id = public.current_user_industry_id()
        OR public.is_admin()
    );

DROP POLICY IF EXISTS "Industries can submit complaint" ON public.complaints;
CREATE POLICY "Industries can submit complaint"
    ON public.complaints FOR INSERT
    TO authenticated
    WITH CHECK (raised_by_industry_id = public.current_user_industry_id());

DROP POLICY IF EXISTS "Admin can update complaints" ON public.complaints;
CREATE POLICY "Admin can update complaints"
    ON public.complaints FOR UPDATE
    TO authenticated
    USING (public.is_admin());

DROP POLICY IF EXISTS "Users can insert feedback" ON public.platform_feedback;
CREATE POLICY "Users can insert feedback"
    ON public.platform_feedback FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Admin can view feedback" ON public.platform_feedback;
CREATE POLICY "Admin can view feedback"
    ON public.platform_feedback FOR SELECT
    TO authenticated
    USING (public.is_admin());

-- ---------------------------------------------------------------------
-- 12. Audit Logs & Security
-- ---------------------------------------------------------------------
DROP POLICY IF EXISTS "Admin can view audit logs" ON public.audit_logs;
CREATE POLICY "Admin can view audit logs"
    ON public.audit_logs FOR SELECT
    TO authenticated
    USING (public.is_admin());

DROP POLICY IF EXISTS "Admin can view and update fraud flags" ON public.fraud_flags;
CREATE POLICY "Admin can view and update fraud flags"
    ON public.fraud_flags FOR ALL
    TO authenticated
    USING (public.is_admin());
