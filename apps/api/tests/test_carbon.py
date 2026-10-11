from app.services.carbon import compute_esg_impact

def test_carbon_and_landfill_calculation():
    # 50 tons with emission factor 1150 kg CO2/ton
    result = compute_esg_impact(
        quantity_tons=50.0,
        emission_factor_kg_per_ton=1150.0,
        landfill_factor=1.0,
        agreed_price_per_ton=1800.0,
        virgin_reference_price_per_ton=2500.0
    )

    assert result["co2_saved_kg"] == 57500.0
    assert result["co2_saved_tonnes"] == 57.5
    assert result["landfill_diverted_kg"] == 50000.0
    assert result["landfill_diverted_tonnes"] == 50.0
    assert result["buyer_savings_inr"] == (2500.0 - 1800.0) * 50.0
    assert result["seller_revenue_inr"] == 1800.0 * 50.0
