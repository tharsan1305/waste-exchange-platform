from app.services.fraud import evaluate_price_anomaly, evaluate_reused_document_hash

def test_fraud_price_anomaly():
    median = 1000.0

    # Normal price (no alert)
    assert evaluate_price_anomaly(950.0, median) is None

    # Severely underpriced (dumping)
    dump_alert = evaluate_price_anomaly(200.0, median)
    assert dump_alert is not None
    assert dump_alert["rule_code"] == "PRICE_ANOMALY_SUB_MARKET"

    # Extreme price gouging
    gouge_alert = evaluate_price_anomaly(3500.0, median)
    assert gouge_alert is not None
    assert gouge_alert["rule_code"] == "PRICE_ANOMALY_PRICE_GOUGING"

def test_fraud_reused_document_hash():
    sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    existing_map = {sha: "industry_abc"}

    # Same industry uploading again -> no fraud
    assert evaluate_reused_document_hash(sha, existing_map, "industry_abc") is None

    # Different industry uploading same document -> critical fraud!
    fraud = evaluate_reused_document_hash(sha, existing_map, "industry_xyz")
    assert fraud is not None
    assert fraud["rule_code"] == "DOCUMENT_HASH_REUSE"
    assert fraud["severity"] == "critical"
