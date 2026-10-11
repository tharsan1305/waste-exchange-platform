-- =====================================================================
-- Migration 01: Extensions and Domain ENUM Types
-- Platform: Supabase PostgreSQL
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- User and Industry Roles
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'industry_admin', 'industry_staff');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE verification_status AS ENUM ('pending', 'approved', 'rejected', 'suspended');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE industry_doc_type AS ENUM ('gst', 'license', 'pcb_auth', 'other');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Waste & Listings
DO $$ BEGIN
    CREATE TYPE waste_unit AS ENUM ('kg', 'ton');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE recurrence_type AS ENUM ('weekly', 'monthly', 'quarterly');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE listing_status AS ENUM ('available', 'reserved', 'sold', 'expired', 'removed', 'flagged');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE listing_doc_type AS ENUM ('lab_report', 'manifest', 'other');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Requests & RFQ
DO $$ BEGIN
    CREATE TYPE request_status AS ENUM ('open', 'accepted', 'rejected', 'withdrawn');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE rfq_status AS ENUM ('open', 'closed', 'awarded');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE rfq_quote_status AS ENUM ('submitted', 'accepted', 'rejected');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Deals & Stages
DO $$ BEGIN
    CREATE TYPE deal_stage AS ENUM (
        'negotiation',
        'agreed',
        'payment_confirmed',
        'pickup_scheduled',
        'delivered',
        'completed',
        'cancelled',
        'disputed'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'disputed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Notifications & Feedback
DO $$ BEGIN
    CREATE TYPE notification_channel AS ENUM ('in_app', 'email', 'sms');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE notification_status AS ENUM ('queued', 'sent', 'failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE sentiment_label AS ENUM ('positive', 'neutral', 'negative');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Complaints & Quality
DO $$ BEGIN
    CREATE TYPE complaint_type AS ENUM ('wrong_waste', 'payment_issue', 'fake_listing', 'other');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE complaint_status AS ENUM ('open', 'in_review', 'resolved', 'rejected');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE feedback_type AS ENUM ('bug', 'suggestion', 'other');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Fraud & Security
DO $$ BEGIN
    CREATE TYPE fraud_severity AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE fraud_status AS ENUM ('open', 'dismissed', 'confirmed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
