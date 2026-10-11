from app.services.matching import compute_match_score

def test_rule_based_matching_perfect_synergy():
    # Listing: Sugar mill bagasse in Namakkal
    listing = {
        "lat": 11.0827,
        "lng": 78.1436,
        "quantity": 50.0,
        "is_hazardous": False
    }

    # Candidate: Paper Mill in Karur (approx 20 km away)
    candidate_paper_mill = {
        "id": "cand-001",
        "name": "TNPL Karur Paper Plant",
        "industry_type": "Paper Mill",
        "lat": 10.9856,
        "lng": 78.0264,
        "trust_score": 4.9,
        "pcb_authorization_no": "PCB/KR/01"
    }

    usage_rules = [
        {"industry_type": "Paper Mill", "use_case": "Virgin fiber replacement"}
    ]

    result = compute_match_score(listing, candidate_paper_mill, usage_rules)

    assert result["is_compatible"] is True
    assert result["total_match_score"] >= 85.0
    assert result["breakdown"]["compatibility_score"] == 40.0
    assert result["breakdown"]["hazard_compliance_score"] == 10.0
    assert result["breakdown"]["quantity_score"] == 15.0

def test_rule_based_matching_incompatible_hazard():
    # Hazardous spent acid
    listing = {
        "lat": 11.0,
        "lng": 78.0,
        "quantity": 20.0,
        "is_hazardous": True
    }

    # Candidate lacks PCB authorization
    candidate_unauthorized = {
        "id": "cand-002",
        "name": "Local Brick Kiln",
        "industry_type": "Brick Manufacturing",
        "lat": 11.1,
        "lng": 78.1,
        "trust_score": 4.0,
        "pcb_authorization_no": None  # NO PCB AUTH
    }

    usage_rules = []
    result = compute_match_score(listing, candidate_unauthorized, usage_rules)

    # Hazard compliance score must be 0 because candidate lacks authorization
    assert result["breakdown"]["hazard_compliance_score"] == 0.0
    assert result["is_compatible"] is False
