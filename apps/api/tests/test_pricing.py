from app.services.pricing import calculate_pricing_suggestions

def test_pricing_suggestions_with_data():
    prices = [600.0, 650.0, 700.0, 750.0, 800.0]
    result = calculate_pricing_suggestions(prices)

    assert result["median_price"] == 700.0
    assert result["average_price"] == 700.0
    assert result["sample_size"] == 5
    assert result["confidence"] == "high"

def test_pricing_suggestions_fallback():
    result = calculate_pricing_suggestions([], default_fallback_price=1200.0)

    assert result["suggested_price"] == 1200.0
    assert result["sample_size"] == 0
    assert result["confidence"] == "baseline_estimate"
