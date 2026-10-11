-- =====================================================================
-- Seed Data: Waste Exchange Platform (Industrial Symbiosis) (Idempotent)
-- All UUIDs are valid hex characters [0-9a-f]
-- =====================================================================

-- 1. Trust Badges
INSERT INTO public.badges (id, code, name, description) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'verified', 'Verified Industry', 'Official GST, trade license, and pollution board authorization verified by platform admin.'),
    ('b0000000-0000-0000-0000-000000000002', 'top_seller', 'Top Circular Supplier', 'Consistently delivers high-spec byproducts with >95% deal fulfillment rate.'),
    ('b0000000-0000-0000-0000-000000000003', 'eco_partner', 'Eco Sustainability Partner', 'Over 100 tonnes of industrial waste diverted from regional landfills.')
ON CONFLICT (id) DO NOTHING;

-- 2. Waste Categories
INSERT INTO public.waste_categories (id, name, description) VALUES
    ('c0000000-0000-0000-0000-000000000001', 'Organic & Biomass', 'Agricultural residue, mill pulp, bagasse, and press mud.'),
    ('c0000000-0000-0000-0000-000000000002', 'Ash & Mineral Byproducts', 'Fly ash, bottom ash, boiler cinders, and mineral tailings.'),
    ('c0000000-0000-0000-0000-000000000003', 'Slag & Metallurgical Waste', 'Blast furnace slag, steel slag, foundry sand, and off-cuts.'),
    ('c0000000-0000-0000-0000-000000000004', 'Chemical & Industrial Sludge', 'Spent acids, lime sludge, phosphogypsum, and spent oils.'),
    ('c0000000-0000-0000-0000-000000000005', 'Plastic & Synthetic Scrap', 'Post-industrial HDPE, LDPE, PET runners, and clean regrind.'),
    ('c0000000-0000-0000-0000-000000000006', 'Wood & Fiber Off-cuts', 'Sawdust, timber shavings, and textile ginning cotton lint.')
ON CONFLICT (id) DO NOTHING;

-- 3. 15 Waste Types (Valid Hex UUIDs: a1000000-...)
INSERT INTO public.waste_types (id, category_id, name, is_hazardous_default) VALUES
    ('a1000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'Sugar Mill Bagasse', FALSE),
    ('a1000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000002', 'Thermal Power Fly Ash (Class F)', FALSE),
    ('a1000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000002', 'Boiler Coal Bottom Ash', FALSE),
    ('a1000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000003', 'Steel Converter Slag', FALSE),
    ('a1000000-0000-0000-0000-000000000005', 'c0000000-0000-0000-0000-000000000006', 'Sawdust & Wood Shavings', FALSE),
    ('a1000000-0000-0000-0000-000000000006', 'c0000000-0000-0000-0000-000000000004', 'Used Industrial Lubricating Oil', TRUE),
    ('a1000000-0000-0000-0000-000000000007', 'c0000000-0000-0000-0000-000000000003', 'Post-Industrial Scrap Steel Sheets', FALSE),
    ('a1000000-0000-0000-0000-000000000008', 'c0000000-0000-0000-0000-000000000005', 'Post-Industrial HDPE / PET Scrap', FALSE),
    ('a1000000-0000-0000-0000-000000000009', 'c0000000-0000-0000-0000-000000000001', 'Distillery Press Mud & Spent Wash', FALSE),
    ('a1000000-0000-0000-0000-000000000010', 'c0000000-0000-0000-0000-000000000001', 'Rice Husk & Husk Ash', FALSE),
    ('a1000000-0000-0000-0000-000000000011', 'c0000000-0000-0000-0000-000000000004', 'Spent Pickling Acid (HCl / H2SO4)', TRUE),
    ('a1000000-0000-0000-0000-000000000012', 'c0000000-0000-0000-0000-000000000006', 'Cotton Ginning Trash & Textile Lint', FALSE),
    ('a1000000-0000-0000-0000-000000000013', 'c0000000-0000-0000-0000-000000000004', 'Paper Mill Lime Sludge', FALSE),
    ('a1000000-0000-0000-0000-000000000014', 'c0000000-0000-0000-0000-000000000004', 'Chemical Phosphogypsum', FALSE),
    ('a1000000-0000-0000-0000-000000000015', 'c0000000-0000-0000-0000-000000000003', 'Foundry Core Sand', FALSE)
ON CONFLICT (id) DO NOTHING;

-- 4. Waste Usage Rules
INSERT INTO public.waste_usage_rules (waste_type_id, industry_type, use_case, priority) VALUES
    ('a1000000-0000-0000-0000-000000000001', 'Paper Mill', 'Fiber replacement for virgin wood pulp in kraft paper', 1),
    ('a1000000-0000-0000-0000-000000000001', 'Biofuel & Pellet Unit', 'Biomass briquettes and bio-ethanol feed', 1),
    ('a1000000-0000-0000-0000-000000000001', 'Molded Fiber Packaging', 'Biodegradable tableware and protective packaging', 2),
    ('a1000000-0000-0000-0000-000000000002', 'Cement Factory', 'Pozzolanic raw material replacing clinker in PPC cement', 1),
    ('a1000000-0000-0000-0000-000000000002', 'Brick Manufacturing', 'Fly ash brick molding and autoclaved aerated concrete (AAC)', 1),
    ('a1000000-0000-0000-0000-000000000002', 'Ready Mix Concrete', 'High performance mineral admixture', 2),
    ('a1000000-0000-0000-0000-000000000003', 'Road Construction', 'Embankment and granular sub-base fill', 1),
    ('a1000000-0000-0000-0000-000000000004', 'Highway Construction', 'Bituminous road aggregate and sub-base layer', 1),
    ('a1000000-0000-0000-0000-000000000004', 'Cement Factory', 'Portland Slag Cement (PSC) raw mix constituent', 1),
    ('a1000000-0000-0000-0000-000000000005', 'Wood Particle Board', 'Engineered MDF boards and composite panels', 1),
    ('a1000000-0000-0000-0000-000000000005', 'Activated Carbon Unit', 'High porosity carbon adsorbent precursor', 2),
    ('a1000000-0000-0000-0000-000000000006', 'Re-Refining & Lubricants', 'Base oil recovery and distillation', 1),
    ('a1000000-0000-0000-0000-000000000007', 'Foundry & Mini Steel Mill', 'Electric arc furnace scrap melting', 1),
    ('a1000000-0000-0000-0000-000000000008', 'Plastic Granulation & Molding', 'Extruded recycled pellets and industrial crates', 1),
    ('a1000000-0000-0000-0000-000000000009', 'Bio-Fertilizer & Compost', 'Soil conditioner and organic microbial compost', 1),
    ('a1000000-0000-0000-0000-000000000010', 'Thermal Boilers', 'Combustion fuel alternative to bituminous coal', 1),
    ('a1000000-0000-0000-0000-000000000011', 'Effluent Neutralization Plant', 'pH neutralization and ferric coagulant production', 1),
    ('a1000000-0000-0000-0000-000000000013', 'Cement Factory', 'Lime source replacement in raw meal feed', 1),
    ('a1000000-0000-0000-0000-000000000014', 'Plasterboard & Wall Panels', 'Gypsum board core substitute for mineral gypsum', 1)
ON CONFLICT (id) DO NOTHING;

-- 5. Emission Factors
INSERT INTO public.emission_factors (waste_type_id, kg_co2e_avoided_per_ton, landfill_factor, source_note) VALUES
    ('a1000000-0000-0000-0000-000000000001', 1150.00, 1.00, 'Avoids open field burning and virgin pulp harvesting (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000002', 820.00, 1.00, 'Replaces clinker calcination in Portland Pozzolana Cement (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000003', 450.00, 1.00, 'Diverts boiler ash from ash ponds into road stabilization (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000004', 650.00, 1.00, 'Avoids virgin quarry aggregate blasting and crushing (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000005', 920.00, 1.00, 'Biomass carbon sequestration in engineered wood (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000006', 1850.00, 1.00, 'Avoids crude virgin lubricant drilling and soil toxicity (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000007', 1600.00, 1.00, 'Electric arc furnace recycling vs primary blast furnace ore (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000008', 1750.00, 1.00, 'Replaces virgin petrochemical ethylene/naphtha cracking (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000009', 750.00, 1.00, 'Eliminates methane release from anaerobic lagoon dumping (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000010', 980.00, 1.00, 'Direct coal offset in agro-processing steam boilers (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000011', 1450.00, 1.00, 'Hazardous neutralizer recovery preventing soil salinization (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000012', 680.00, 1.00, 'Natural cellulosic fiber reuse in paper and spun yarn (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000013', 540.00, 1.00, 'Avoids virgin limestone quarrying and calcining energy (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000014', 420.00, 1.00, 'Replaces mined gypsum in gypsum plasterboard (Illustrative benchmark)'),
    ('a1000000-0000-0000-0000-000000000015', 380.00, 1.00, 'Avoids fresh silica sand mining and thermal drying (Illustrative benchmark)')
ON CONFLICT (waste_type_id) DO NOTHING;

-- 6. Demo Industries across Tamil Nadu (Valid Hex UUIDs: f1000000-...)
INSERT INTO public.industries (id, name, gst_number, license_number, industry_type, address, city, state, pincode, lat, lng, contact_email, contact_phone, verification_status, trust_score, pcb_authorization_no) VALUES
    ('f1000000-0000-0000-0000-000000000001', 'Cauvery Sugar Mills Ltd', '33AABCC1234F1Z1', 'FAC-TN-2021-098', 'Sugar Mill', 'Sugar Factory Road, Mohanur', 'Namakkal', 'Tamil Nadu', '637015', 11.0827, 78.1436, 'ops@cauverysugar.com', '+91 98401 23456', 'approved', 4.90, 'PCB/NM/SMR-2023-41'),
    ('f1000000-0000-0000-0000-000000000002', 'TNPL Karur Paper Plant', '33AAACT9876K1Z9', 'FAC-TN-2019-451', 'Paper Mill', 'Kagithapuram', 'Karur', 'Tamil Nadu', '639136', 10.9856, 78.0264, 'procurement@tnplkarur.in', '+91 98402 34567', 'approved', 4.95, 'PCB/KR/PPR-2022-12'),
    ('f1000000-0000-0000-0000-000000000003', 'Mettur Thermal Power Station', '33AABCT5544P1Z3', 'FAC-TN-2018-882', 'Thermal Power Plant', 'Thermal Power Complex, Mettur Dam', 'Salem', 'Tamil Nadu', '636406', 11.7865, 77.8012, 'ash.mgmt@metturpower.gov.in', '+91 98403 45678', 'approved', 4.80, 'PCB/SLM/TPS-2024-89'),
    ('f1000000-0000-0000-0000-000000000004', 'Dalmia Cement Bharat Ltd', '33AABCD1122D1Z5', 'FAC-TN-2020-112', 'Cement Factory', 'Dalmiapuram', 'Tiruchirappalli', 'Tamil Nadu', '621651', 10.9634, 78.8541, 'rawmaterials@dalmiacement.com', '+91 98404 56789', 'approved', 4.92, 'PCB/TRY/CMT-2023-77'),
    ('f1000000-0000-0000-0000-000000000005', 'Coimbatore AAC Eco-Bricks', '33AABCC7788M1Z8', 'FAC-TN-2022-303', 'Brick Manufacturing', 'Neelambur Industrial Estate', 'Coimbatore', 'Tamil Nadu', '641062', 11.0583, 77.0864, 'contact@coimbatorebricks.com', '+91 98405 67890', 'approved', 4.75, 'PCB/CBE/BRK-2023-15'),
    ('f1000000-0000-0000-0000-000000000006', 'Jindal Steels Salem Works', '33AABCJ3344J1Z2', 'FAC-TN-2017-640', 'Foundry & Mini Steel Mill', 'Steel Plant Road', 'Salem', 'Tamil Nadu', '636013', 11.6643, 78.0772, 'byproducts@jindalsalem.in', '+91 98406 78901', 'approved', 4.88, 'PCB/SLM/STL-2021-99'),
    ('f1000000-0000-0000-0000-000000000007', 'Madurai Eco Synthetics & Polymers', '33AABCM9900L1Z4', 'FAC-TN-2023-019', 'Plastic Granulation & Molding', 'Kappalur SIDCO Industrial Estate', 'Madurai', 'Tamil Nadu', '625008', 9.8512, 78.0543, 'recycle@maduraipolymers.com', '+91 98407 89012', 'approved', 4.70, 'PCB/MDU/PLS-2023-08'),
    ('f1000000-0000-0000-0000-000000000008', 'Tuticorin Bio-Chemical Solutions', '33AABCT6677T1Z6', 'FAC-TN-2021-508', 'Effluent Neutralization Plant', 'SIPCOT Industrial Complex', 'Tuticorin', 'Tamil Nadu', '628008', 8.7642, 78.1348, 'ops@tuticorinbio.com', '+91 98408 90123', 'pending', 5.00, 'PCB/TUT/CHM-2024-03')
ON CONFLICT (id) DO NOTHING;

-- Award Badges
INSERT INTO public.industry_badges (industry_id, badge_id) VALUES
    ('f1000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001'),
    ('f1000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000003'),
    ('f1000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000001'),
    ('f1000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000002'),
    ('f1000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000001'),
    ('f1000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000003'),
    ('f1000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000001')
ON CONFLICT (industry_id, badge_id) DO NOTHING;

-- 7. Demo Waste Listings (Valid Hex UUIDs: e1000000-...)
INSERT INTO public.waste_listings (id, industry_id, waste_type_id, title, description, quantity, unit, price_per_unit, currency, is_hazardous, is_recurring, recurrence, expires_at, status, batch_code, lat, lng, quality_params) VALUES
    ('e1000000-0000-0000-0000-000000000001', 'f1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'Dry Crushed Bagasse Fiber (Low Moisture)', 'High fiber sugar mill bagasse suitable for kraft paper and biofuel briquettes.', 50.00, 'ton', 1800.00, 'INR', FALSE, TRUE, 'weekly', NOW() + INTERVAL '30 days', 'available', 'BAGASSE-2026-NMK-01', 11.0827, 78.1436, '{"moisture_pct": 12.5, "fiber_purity_pct": 98.2, "calorific_value_kcal_kg": 2200}'::jsonb),
    ('e1000000-0000-0000-0000-000000000002', 'f1000000-0000-0000-0000-000000000003', 'a1000000-0000-0000-0000-000000000002', 'Class-F Pozzolanic Fly Ash (Silo Conditioned)', 'Dry pulverized coal fly ash conforming to IS:3812 Part 1 for Portland Pozzolana Cement.', 120.00, 'ton', 650.00, 'INR', FALSE, TRUE, 'weekly', NOW() + INTERVAL '45 days', 'available', 'FLYASH-2026-MTR-02', 11.7865, 77.8012, '{"fineness_m2_kg": 340, "sio2_plus_al2o3_pct": 74.5, "loss_on_ignition_pct": 2.1}'::jsonb),
    ('e1000000-0000-0000-0000-000000000003', 'f1000000-0000-0000-0000-000000000006', 'a1000000-0000-0000-0000-000000000004', 'Crushed Steel Converter Slag Aggregates', 'Dense air-cooled steel slag aggregate suitable for flexible pavement sub-base.', 80.00, 'ton', 420.00, 'INR', FALSE, FALSE, NULL, NOW() + INTERVAL '20 days', 'available', 'SLAG-2026-SLM-03', 11.6643, 78.0772, '{"aggregate_impact_value_pct": 18, "specific_gravity": 3.2}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- 8. Demo Deals (Valid Hex UUIDs: d1000000-...)
INSERT INTO public.deals (id, listing_id, seller_industry_id, buyer_industry_id, quantity, agreed_price_per_unit, total_amount, stage, payment_status, vehicle_number, transporter_name, co2_saved_kg, landfill_diverted_kg, money_saved) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', 'f1000000-0000-0000-0000-000000000001', 'f1000000-0000-0000-0000-000000000002', 40.00, 1750.00, 70000.00, 'completed', 'paid', 'TN-28-AK-8899', 'Kongu Heavy Roadlines', 46000.00, 40000.00, 32000.00),
    ('d1000000-0000-0000-0000-000000000002', 'e1000000-0000-0000-0000-000000000002', 'f1000000-0000-0000-0000-000000000003', 'f1000000-0000-0000-0000-000000000004', 60.00, 600.00, 36000.00, 'completed', 'paid', 'TN-30-X-4512', 'Mettur Bulk Carriers', 49200.00, 60000.00, 24000.00),
    ('d1000000-0000-0000-0000-000000000003', 'e1000000-0000-0000-0000-000000000002', 'f1000000-0000-0000-0000-000000000003', 'f1000000-0000-0000-0000-000000000005', 25.00, 620.00, 15500.00, 'agreed', 'pending', 'TN-38-BZ-1002', 'Coimbatore Express Transport', 0.00, 0.00, 0.00)
ON CONFLICT (id) DO NOTHING;

-- Stage History
INSERT INTO public.deal_stage_history (deal_id, from_stage, to_stage, note) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'negotiation', 'agreed', 'Price agreed at INR 1750/ton for 40 tons.'),
    ('d1000000-0000-0000-0000-000000000001', 'agreed', 'payment_confirmed', 'Bank RTGS transfer verified.'),
    ('d1000000-0000-0000-0000-000000000001', 'payment_confirmed', 'pickup_scheduled', 'Truck TN-28-AK-8899 assigned.'),
    ('d1000000-0000-0000-0000-000000000001', 'pickup_scheduled', 'delivered', 'Consignment received at Karur factory gate.'),
    ('d1000000-0000-0000-0000-000000000001', 'delivered', 'completed', 'Quality verified. 46 tons CO2 avoided recorded.')
ON CONFLICT (id) DO NOTHING;

-- 9. Completed Reviews
INSERT INTO public.reviews (deal_id, reviewer_industry_id, reviewee_industry_id, rating, quality, quantity, on_time_delivery, communication, comment, sentiment, sentiment_score) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'f1000000-0000-0000-0000-000000000002', 'f1000000-0000-0000-0000-000000000001', 5, 5, 5, 5, 5, 'High fiber bagasse with exact moisture specs as mentioned. Fast dispatch and smooth weighing slip sharing.', 'positive', 0.95)
ON CONFLICT (deal_id, reviewer_industry_id) DO NOTHING;
