from typing import Dict, Any

def compute_esg_impact(
    quantity_tons: float,
    emission_factor_kg_per_ton: float,
    landfill_factor: float = 1.0,
    agreed_price_per_ton: float = 0.0,
    virgin_reference_price_per_ton: float = 0.0
) -> Dict[str, Any]:
    """
    Computes ESG sustainability and economic impact metrics:
    - CO2e emissions avoided (in kilograms and tonnes)
    - Landfill diversion (in kilograms and tonnes)
    - Buyer raw material cost savings (in INR)
    - Seller byproduct revenue (in INR)
    """
    co2_saved_kg = round(quantity_tons * emission_factor_kg_per_ton, 2)
    landfill_diverted_kg = round(quantity_tons * 1000.0 * landfill_factor, 2)

    # Money saved calculation
    if virgin_reference_price_per_ton > agreed_price_per_ton:
        buyer_savings_inr = round((virgin_reference_price_per_ton - agreed_price_per_ton) * quantity_tons, 2)
    else:
        buyer_savings_inr = 0.0

    seller_revenue_inr = round(agreed_price_per_ton * quantity_tons, 2)

    return {
        "quantity_tons": quantity_tons,
        "co2_saved_kg": co2_saved_kg,
        "co2_saved_tonnes": round(co2_saved_kg / 1000.0, 3),
        "landfill_diverted_kg": landfill_diverted_kg,
        "landfill_diverted_tonnes": round(landfill_diverted_kg / 1000.0, 2),
        "buyer_savings_inr": buyer_savings_inr,
        "seller_revenue_inr": seller_revenue_inr
    }
