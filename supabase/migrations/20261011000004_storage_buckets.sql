-- =====================================================================
-- Migration 04: Supabase Storage Buckets & Storage RLS Policies
-- Platform: Supabase Storage
-- =====================================================================

-- Insert Storage Buckets into storage.buckets if they do not exist
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
    ('industry-docs', 'industry-docs', FALSE, 10485760, ARRAY['application/pdf', 'image/png', 'image/jpeg']),
    ('listing-media', 'listing-media', TRUE, 10485760, ARRAY['image/png', 'image/jpeg', 'image/webp', 'application/pdf']),
    ('manifests', 'manifests', FALSE, 10485760, ARRAY['application/pdf']),
    ('qr-codes', 'qr-codes', TRUE, 2097152, ARRAY['image/png', 'image/svg+xml'])
ON CONFLICT (id) DO UPDATE SET
    public = EXCLUDED.public,
    file_size_limit = EXCLUDED.file_size_limit,
    allowed_mime_types = EXCLUDED.allowed_mime_types;

-- Storage Object Level Security Policies

-- 1. industry-docs bucket (private)
CREATE POLICY "Admins or owners can read industry documents"
    ON storage.objects FOR SELECT
    TO authenticated
    USING (
        bucket_id = 'industry-docs' 
        AND (
            public.is_admin() 
            OR (storage.foldername(name))[1] = public.current_user_industry_id()::text
        )
    );

CREATE POLICY "Authenticated users can upload to their industry folder"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'industry-docs' 
        AND (storage.foldername(name))[1] = public.current_user_industry_id()::text
    );

-- 2. listing-media bucket (public read)
CREATE POLICY "Anyone can view listing media"
    ON storage.objects FOR SELECT
    TO public
    USING (bucket_id = 'listing-media');

CREATE POLICY "Approved industries can upload listing media"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'listing-media' 
        AND public.is_approved_industry()
    );

-- 3. manifests bucket (private)
CREATE POLICY "Deal participants or admin can read manifests"
    ON storage.objects FOR SELECT
    TO authenticated
    USING (
        bucket_id = 'manifests' 
        AND (
            public.is_admin() 
            OR EXISTS (
                SELECT 1 FROM public.manifests m
                JOIN public.deals d ON m.deal_id = d.id
                WHERE m.pdf_path LIKE '%' || storage.objects.name || '%'
                AND (d.seller_industry_id = public.current_user_industry_id() 
                     OR d.buyer_industry_id = public.current_user_industry_id())
            )
        )
    );

-- 4. qr-codes bucket (public read)
CREATE POLICY "Anyone can view qr-codes"
    ON storage.objects FOR SELECT
    TO public
    USING (bucket_id = 'qr-codes');
