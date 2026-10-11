from typing import Dict, Any, List
from app.services.geo import haversine_distance

def compute_match_score(
    listing: Dict[str, Any],
    candidate_industry: Dict[str, Any],
    usage_rules: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Computes deterministic match score (0 to 100) between a byproduct listing
    and a candidate manufacturing facility based on 5 weighted pillars:
    - Waste Compatibility Rule: 40 points
    - Distance: 25 points
    - Quantity Fit: 15 points
    - PCB Hazardous Authorization: 10 points
    - Trust Score: 10 points
    """
    scores = {}

    # 1. Compatibility Rule Check (Weight: 40)
    industry_type = candidate_industry.get("industry_type", "")
    rule_match = any(
        rule.get("industry_type", "").lower() == industry_type.lower()
        for rule in usage_rules
    )
    scores["compatibility_score"] = 40.0 if rule_match else 5.0

    # 2. Distance Score (Weight: 25)
    listing_lat = listing.get("lat", 0.0)
    listing_lng = listing.get("lng", 0.0)
    cand_lat = candidate_industry.get("lat", 0.0)
    cand_lng = candidate_industry.get("lng", 0.0)

    dist_km = haversine_distance(listing_lat, listing_lng, cand_lat, cand_lng)
    scores["distance_km"] = dist_km

    # Proximity decay: 25 pts under 30km, scaling down to 0 at 300km
    if dist_km <= 30.0:
        scores["distance_score"] = 25.0
    elif dist_km >= 300.0:
        scores["distance_score"] = 0.0
    else:
        scores["distance_score"] = round(25.0 * (1.0 - (dist_km - 30.0) / 270.0), 2)

    # 3. Quantity Fit (Weight: 15)
    # Assumes commercial viability starts from minimum batches
    listing_qty = float(listing.get("quantity", 0.0))
    if listing_qty >= 10.0:
        scores["quantity_score"] = 15.0
    elif listing_qty > 0.0:
        scores["quantity_score"] = round(15.0 * (listing_qty / 10.0), 2)
    else:
        scores["quantity_score"] = 0.0

    # 4. Hazardous PCB Authorization Compatibility (Weight: 10)
    is_hazardous = listing.get("is_hazardous", False)
    has_pcb_auth = bool(candidate_industry.get("pcb_authorization_no"))
    if not is_hazardous:
        scores["hazard_compliance_score"] = 10.0
    elif is_hazardous and has_pcb_auth:
        scores["hazard_compliance_score"] = 10.0
    else:
        scores["hazard_compliance_score"] = 0.0  # Cannot legally receive hazardous byproduct

    # 5. Trust Score (Weight: 10)
    raw_trust = float(candidate_industry.get("trust_score", 5.0))  # Scale 1 to 5
    scores["trust_score"] = round((raw_trust / 5.0) * 10.0, 2)

    # Total Score
    total = sum([
        scores["compatibility_score"],
        scores["distance_score"],
        scores["quantity_score"],
        scores["hazard_compliance_score"],
        scores["trust_score"]
    ])
    total_score = min(max(round(total, 1), 0.0), 100.0)

    return {
        "candidate_industry_id": candidate_industry.get("id"),
        "candidate_name": candidate_industry.get("name"),
        "candidate_type": industry_type,
        "total_match_score": total_score,
        "is_compatible": rule_match,
        "breakdown": scores
    }
