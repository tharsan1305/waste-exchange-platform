from typing import Dict, Any, Optional

def evaluate_price_anomaly(price: float, median_price: float) -> Optional[Dict[str, Any]]:
    """
    Flags prices that deviate wildly from fair market median:
    Less than 30% of median (dumping / deceptive) or over 300% (gouging).
    """
    if median_price <= 0:
        return None

    ratio = price / median_price
    if ratio < 0.30:
        return {
            "rule_code": "PRICE_ANOMALY_SUB_MARKET",
            "severity": "medium",
            "details": {
                "price": price,
                "median_price": median_price,
                "deviation_ratio": round(ratio, 2),
                "reason": "Listed price is over 70% below prevailing market median."
            }
        }
    elif ratio > 3.00:
        return {
            "rule_code": "PRICE_ANOMALY_PRICE_GOUGING",
            "severity": "medium",
            "details": {
                "price": price,
                "median_price": median_price,
                "deviation_ratio": round(ratio, 2),
                "reason": "Listed price is more than 300% above prevailing market median."
            }
        }
    return None

def evaluate_reused_document_hash(sha256_hash: str, existing_hashes_map: Dict[str, str], current_industry_id: str) -> Optional[Dict[str, Any]]:
    """
    Detects if the same document hash was already uploaded by a DIFFERENT industry.
    """
    owner_id = existing_hashes_map.get(sha256_hash)
    if owner_id and owner_id != current_industry_id:
        return {
            "rule_code": "DOCUMENT_HASH_REUSE",
            "severity": "critical",
            "details": {
                "sha256_hash": sha256_hash,
                "reused_from_industry_id": owner_id,
                "reason": "Cryptographic file hash matches an existing document uploaded by a separate entity."
            }
        }
    return None

def evaluate_listing_velocity(count_last_hour: int, hourly_limit: int = 15) -> Optional[Dict[str, Any]]:
    """Flags high-frequency automated listing spam."""
    if count_last_hour > hourly_limit:
        return {
            "rule_code": "LISTING_VELOCITY_SPAM",
            "severity": "high",
            "details": {
                "count_last_hour": count_last_hour,
                "limit": hourly_limit,
                "reason": "Listing creation velocity exceeds normal manual limits."
            }
        }
    return None
