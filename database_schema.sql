-- =====================================================================
-- Waste Exchange Platform (Industrial Symbiosis / B2B Waste Exchange)
-- Database Engine: MySQL 8.0+
-- Character Set: utf8mb4 / Collation: utf8mb4_unicode_ci
-- =====================================================================

CREATE DATABASE IF NOT EXISTS waste_exchange_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE waste_exchange_db;

-- ---------------------------------------------------------------------
-- 1. USERS TABLE (Authentication & Base RBAC)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    role ENUM('admin', 'seller', 'buyer', 'both') NOT NULL DEFAULT 'seller',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_2fa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    two_factor_secret VARCHAR(120) DEFAULT NULL,
    last_login_at DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2. INDUSTRIES TABLE (Profile, GST Verification, Trust Badges, Coordinates)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS industries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    company_name VARCHAR(200) NOT NULL,
    industry_type VARCHAR(100) NOT NULL, -- e.g. Sugar Mill, Thermal Power, Paper Mill, Cement Factory
    registration_no VARCHAR(100) DEFAULT NULL,
    gst_number VARCHAR(15) NOT NULL UNIQUE,
    license_document_url VARCHAR(500) DEFAULT NULL,
    verification_status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    verification_remarks TEXT DEFAULT NULL,
    verified_at DATETIME DEFAULT NULL,
    verified_by_admin_id INT DEFAULT NULL,
    address_line TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    trust_score DECIMAL(3, 2) NOT NULL DEFAULT 5.00, -- Scale 1.00 - 5.00
    trust_badge ENUM('none', 'verified', 'top_seller', 'eco_partner') NOT NULL DEFAULT 'none',
    total_waste_diverted_tonnes DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    total_co2_saved_tonnes DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by_admin_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_industry_gst (gst_number),
    INDEX idx_industry_verification (verification_status),
    INDEX idx_industry_location (city, state),
    INDEX idx_industry_coords (latitude, longitude)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3. WASTE CATEGORIES & RULE-BASED MATCHING CONFIG
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS waste_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE, -- e.g., Bagasse, Fly Ash, Spent Acid, Slag, Scrap Metal, E-Waste
    group_type ENUM('organic', 'chemical', 'metal', 'plastic', 'ash', 'sludge', 'other') NOT NULL,
    description TEXT DEFAULT NULL,
    default_co2_factor_per_tonne DECIMAL(6, 3) NOT NULL DEFAULT 0.850, -- CO2 offset saved per tonne diverted
    potential_buyer_industries TEXT NOT NULL, -- JSON or comma-separated target industry types e.g. "Paper Mill, Biofuel, Packaging"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 4. WASTE LISTINGS TABLE
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS waste_listings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_industry_id INT NOT NULL,
    category_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    is_hazardous BOOLEAN NOT NULL DEFAULT FALSE,
    hazard_class VARCHAR(80) DEFAULT NULL, -- e.g. Corrosive, Flammable, Non-Hazardous
    quantity DECIMAL(12, 2) NOT NULL,
    unit ENUM('tonnes', 'kg', 'litres', 'barrels', 'truckloads') NOT NULL DEFAULT 'tonnes',
    moisture_percentage DECIMAL(5, 2) DEFAULT NULL,
    purity_percentage DECIMAL(5, 2) DEFAULT NULL,
    price_per_unit DECIMAL(12, 2) NOT NULL DEFAULT 0.00, -- 0.00 if giveaway / free for transport
    is_price_negotiable BOOLEAN NOT NULL DEFAULT TRUE,
    supply_frequency ENUM('one_time', 'daily', 'weekly', 'monthly') NOT NULL DEFAULT 'one_time',
    lab_test_report_url VARCHAR(500) DEFAULT NULL,
    photo_url VARCHAR(500) DEFAULT NULL,
    pickup_address TEXT NOT NULL,
    pickup_latitude DECIMAL(10, 7) NOT NULL,
    pickup_longitude DECIMAL(10, 7) NOT NULL,
    status ENUM('active', 'under_negotiation', 'sold', 'archived') NOT NULL DEFAULT 'active',
    views_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_industry_id) REFERENCES industries(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES waste_categories(id) ON DELETE RESTRICT,
    INDEX idx_listing_status (status),
    INDEX idx_listing_hazard (is_hazardous),
    INDEX idx_listing_coords (pickup_latitude, pickup_longitude),
    FULLTEXT INDEX ft_listing_search (title, description)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 5. REQUESTS / QUOTES (Negotiation Stage 1)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    listing_id INT NOT NULL,
    buyer_industry_id INT NOT NULL,
    proposed_quantity DECIMAL(12, 2) NOT NULL,
    offered_price_per_unit DECIMAL(12, 2) NOT NULL,
    transport_responsibility ENUM('buyer_pickup', 'seller_delivery', 'shared_logistics') NOT NULL DEFAULT 'buyer_pickup',
    estimated_distance_km DECIMAL(8, 2) DEFAULT NULL,
    estimated_transport_cost DECIMAL(12, 2) DEFAULT NULL,
    buyer_note TEXT DEFAULT NULL,
    seller_counter_note TEXT DEFAULT NULL,
    status ENUM('pending', 'seller_countered', 'accepted', 'rejected', 'cancelled') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES waste_listings(id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_industry_id) REFERENCES industries(id) ON DELETE CASCADE,
    INDEX idx_request_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 6. DEALS TABLE (Finalized Agreements)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS deals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL UNIQUE,
    listing_id INT NOT NULL,
    seller_industry_id INT NOT NULL,
    buyer_industry_id INT NOT NULL,
    final_quantity DECIMAL(12, 2) NOT NULL,
    final_price_per_unit DECIMAL(12, 2) NOT NULL,
    total_deal_amount DECIMAL(14, 2) NOT NULL,
    transport_mode VARCHAR(100) DEFAULT 'Standard Heavy Haulage',
    expected_dispatch_date DATE DEFAULT NULL,
    actual_delivery_date DATE DEFAULT NULL,
    deal_status ENUM('agreed', 'in_transit', 'delivered', 'completed', 'disputed') NOT NULL DEFAULT 'agreed',
    landfill_diverted_tonnes DECIMAL(12, 2) NOT NULL,
    co2_saved_tonnes DECIMAL(12, 2) NOT NULL,
    completed_at DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE RESTRICT,
    FOREIGN KEY (listing_id) REFERENCES waste_listings(id) ON DELETE RESTRICT,
    FOREIGN KEY (seller_industry_id) REFERENCES industries(id) ON DELETE RESTRICT,
    FOREIGN KEY (buyer_industry_id) REFERENCES industries(id) ON DELETE RESTRICT,
    INDEX idx_deal_status (deal_status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 7. MESSAGES (Direct In-Platform Chat for Negotiations)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    sender_user_id INT NOT NULL,
    receiver_user_id INT NOT NULL,
    message_text TEXT NOT NULL,
    attachment_url VARCHAR(500) DEFAULT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_chat_convo (request_id, created_at)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 8. NOTIFICATIONS (Rule Matching, Quote Updates, Verifications)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    notification_type ENUM('match_alert', 'quote_update', 'verification', 'deal_milestone', 'security_alert') NOT NULL,
    action_url VARCHAR(255) DEFAULT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_notifications (user_id, is_read)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 9. REVIEWS & RATINGS (Post-Deal Feedback & Sentiment)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    deal_id INT NOT NULL,
    reviewer_industry_id INT NOT NULL,
    reviewee_industry_id INT NOT NULL,
    rating_overall TINYINT NOT NULL CHECK (rating_overall BETWEEN 1 AND 5),
    rating_quality TINYINT NOT NULL CHECK (rating_quality BETWEEN 1 AND 5),
    rating_quantity TINYINT NOT NULL CHECK (rating_quantity BETWEEN 1 AND 5),
    rating_delivery TINYINT NOT NULL CHECK (rating_delivery BETWEEN 1 AND 5),
    rating_communication TINYINT NOT NULL CHECK (rating_communication BETWEEN 1 AND 5),
    feedback_comment TEXT DEFAULT NULL,
    sentiment_label ENUM('positive', 'neutral', 'negative') DEFAULT 'positive',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_deal_reviewer (deal_id, reviewer_industry_id),
    FOREIGN KEY (deal_id) REFERENCES deals(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_industry_id) REFERENCES industries(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewee_industry_id) REFERENCES industries(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 10. COMPLAINTS TABLE (Issue Handling & Ticket Resolution)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    deal_id INT DEFAULT NULL,
    complainant_industry_id INT NOT NULL,
    accused_industry_id INT NOT NULL,
    complaint_type ENUM('wrong_waste_spec', 'payment_issue', 'fake_listing', 'toxic_hazardous_mismatch', 'delivery_failure', 'other') NOT NULL,
    description TEXT NOT NULL,
    evidence_document_url VARCHAR(500) DEFAULT NULL,
    status ENUM('open', 'in_review', 'resolved', 'rejected') NOT NULL DEFAULT 'open',
    resolution_notes TEXT DEFAULT NULL,
    resolved_by_admin_id INT DEFAULT NULL,
    resolved_at DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (deal_id) REFERENCES deals(id) ON DELETE SET NULL,
    FOREIGN KEY (complainant_industry_id) REFERENCES industries(id) ON DELETE CASCADE,
    FOREIGN KEY (accused_industry_id) REFERENCES industries(id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by_admin_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_complaint_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 11. PLATFORM FEEDBACK (User Suggestions & Bug Reports)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS platform_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT NULL,
    category ENUM('bug_report', 'feature_request', 'ux_improvement', 'other') NOT NULL DEFAULT 'ux_improvement',
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 12. AUDIT LOGS (Cybersecurity, Non-Repudiation, Forensic Trail)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT NULL,
    action_type VARCHAR(100) NOT NULL, -- e.g. AUTH_LOGIN, VERIFY_APPROVE, POST_LISTING, DEAL_ACCEPTED
    resource_name VARCHAR(100) NOT NULL,
    resource_id INT DEFAULT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent VARCHAR(255) DEFAULT NULL,
    payload_snapshot JSON DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_action (action_type),
    INDEX idx_audit_time (created_at)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- SEED DATA: Waste Categories & Pre-Configured Rule-Based Matching
-- ---------------------------------------------------------------------
INSERT INTO waste_categories (name, group_type, description, default_co2_factor_per_tonne, potential_buyer_industries)
VALUES
('Sugar Mill Bagasse', 'organic', 'Sugarcane pulp remaining after juice extraction. High calorific biomass.', 1.150, 'Paper Mill, Biomass Power Plant, Packaging, Bio-Ethanol'),
('Thermal Power Fly Ash', 'ash', 'Pulverized coal combustion byproduct. Pozzolanic raw material.', 0.820, 'Cement Factory, Ready Mix Concrete, Brick Manufacturing, Road Base'),
('Steel Slag / Foundry Slag', 'metal', 'Byproduct of steel making process. Rich in iron oxides and silicates.', 0.650, 'Cement Factory, Highway Construction, Railway Ballast, Soil Conditioner'),
('Spent Pickling Acid (HCl/H2SO4)', 'chemical', 'Acidic solution from metal surface cleaning. Requires neutralizer/reclaim.', 1.450, 'Effluent Treatment Plant, Chemical Synthesizers, Fertilizer Base'),
('Post-Industrial PET Scrap', 'plastic', 'Clean industrial plastic off-cuts and runners.', 1.750, 'Textile & Synthetic Fiber, Blow Moulding, Packaging Material'),
('Distillery Spent Wash Sludge', 'sludge', 'Concentrated organic residue from fermentation.', 0.950, 'Organic Bio-Compost, Biogas Generator, Boiler Fuel');
