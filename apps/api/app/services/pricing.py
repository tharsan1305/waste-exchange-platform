import statistics
from typing import Dict, Any, List

def calculate_pricing_suggestions(past_prices: List[float], default_fallback_price: float = 1000.0) -> Dict[str, Any]:
    """
    Computes fair market pricing bands from completed transaction records.
    Provides median, average, and a recommended price range.
    """
    valid_prices = [p for p in past_prices if p > 0]

    if not valid_prices:
        return {
            "suggested_price": default_fallback_price,
            "min_band": round(default_fallback_price * 0.85, 2),
            "max_band": round(default_fallback_price * 1.15, 2),
            "median_price": default_fallback_price,
            "average_price": default_fallback_price,
            "sample_size": 0,
            "confidence": "baseline_estimate"
        }

    median_val = statistics.median(valid_prices)
    mean_val = statistics.mean(valid_prices)

    return {
        "suggested_price": round(median_val, 2),
        "min_band": round(min(valid_prices) * 0.95, 2),
        "max_band": round(max(valid_prices) * 1.05, 2),
        "median_price": round(median_val, 2),
        "average_price": round(mean_val, 2),
        "sample_size": len(valid_prices),
        "confidence": "high" if len(valid_prices) >= 5 else "moderate"
    }
