import pytest
import os
import boto3
from moto import mock_aws
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.services.s3_storage import (
    validate_and_upload_to_s3,
    generate_presigned_download_url,
    get_s3_client
)
from app.core.deps import get_current_user

client = TestClient(app)

@pytest.fixture
def s3_setup():
    """Sets up a mocked S3 environment using moto."""
    with mock_aws():
        s3 = boto3.client("s3", region_name=settings.AWS_REGION)
        s3.create_bucket(
            Bucket=settings.S3_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": settings.AWS_REGION}
        )
        yield s3

def test_s3_upload_and_presigned_url(s3_setup):
    """Verifies S3 upload pipeline, encryption, SHA-256 and 5-min presigned URL."""
    test_pdf = b"%PDF-1.4 Mock Industrial GST Registration Document"
    bucket, key, sha256_hash = validate_and_upload_to_s3(
        file_bytes=test_pdf,
        object_key="industries/f1000000-0000-0000-0000-000000000001/gst.pdf",
        content_type="application/pdf"
    )

    assert bucket == settings.S3_BUCKET
    assert key == "industries/f1000000-0000-0000-0000-000000000001/gst.pdf"
    assert len(sha256_hash) == 64

    # Verify object exists in mocked S3 with ServerSideEncryption
    obj = s3_setup.get_object(Bucket=settings.S3_BUCKET, Key=key)
    assert obj["ServerSideEncryption"] == "AES256"
    assert obj["Body"].read() == test_pdf

    # Verify pre-signed URL generation
    presigned_url = generate_presigned_download_url(key, expiration_seconds=300)
    assert "X-Amz-Signature" in presigned_url or "https://" in presigned_url

def test_s3_upload_rejects_invalid_mime_type(s3_setup):
    """Ensures file type allowlist is strictly enforced."""
    with pytest.raises(ValueError, match="is not allowed"):
        validate_and_upload_to_s3(
            file_bytes=b"MALICIOUS_EXECUTABLE",
            object_key="exploit.exe",
            content_type="application/x-msdownload"
        )

def test_s3_upload_rejects_oversized_file(s3_setup):
    """Ensures 10MB size limit is strictly enforced."""
    oversized = b"0" * (10 * 1024 * 1024 + 10)
    with pytest.raises(ValueError, match="exceeds maximum 10MB limit"):
        validate_and_upload_to_s3(
            file_bytes=oversized,
            object_key="big.pdf",
            content_type="application/pdf"
        )

def test_non_approved_industry_cannot_create_listing():
    """
    SECURITY TEST: Proves that an unverified/pending industry CANNOT create listings.
    Must return 403 Forbidden.
    """
    pending_user = {
        "id": "c1000000-0000-0000-0000-000000000099",
        "email": "pending@mill.com",
        "role": "industry_admin",
        "industry": {
            "id": "f1000000-0000-0000-0000-000000000008",
            "name": "Pending Bio-Chemical Solutions",
            "verification_status": "pending"  # PENDING STATUS
        }
    }
    app.dependency_overrides[get_current_user] = lambda: pending_user

    payload = {
        "waste_type_id": "a1000000-0000-0000-0000-000000000001",
        "title": "Unauthorized Listing Test",
        "description": "Should be rejected because industry is not approved.",
        "quantity": 10.0,
        "unit": "ton",
        "price_per_unit": 500.0,
        "is_hazardous": False,
        "expires_at": "2026-11-01T00:00:00Z",
        "lat": 11.0,
        "lng": 78.0
    }

    response = client.post("/api/v1/listings", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert "verification status is 'pending'" in response.json()["error"]["message"]

def test_approved_industry_can_create_listing():
    """
    Verifies that an APPROVED industry passes the security guard and creates listing.
    """
    approved_user = {
        "id": "c1000000-0000-0000-0000-000000000001",
        "email": "ops@cauverysugar.com",
        "role": "industry_admin",
        "industry": {
            "id": "f1000000-0000-0000-0000-000000000001",
            "name": "Cauvery Sugar Mills Ltd",
            "verification_status": "approved",
            "pcb_authorization_no": "PCB/NM/SMR-2023-41"
        }
    }
    app.dependency_overrides[get_current_user] = lambda: approved_user

    payload = {
        "waste_type_id": "a1000000-0000-0000-0000-000000000001",
        "title": "Fresh Wet Bagasse Lot - Approved Test",
        "description": "Valid listing from an approved facility.",
        "quantity": 25.0,
        "unit": "ton",
        "price_per_unit": 1200.0,
        "is_hazardous": False,
        "expires_at": "2026-11-01T00:00:00Z",
        "lat": 11.0827,
        "lng": 78.1436
    }

    response = client.post("/api/v1/listings", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["success"] is True

def test_tenant_isolation_cannot_read_another_industrys_documents(s3_setup):
    """
    SECURITY TEST: Proves that Industry B CANNOT generate presigned download URL
    or read Industry A's private documents. Returns 403 Forbidden.
    """
    user_industry_b = {
        "id": "c1000000-0000-0000-0000-000000000002",
        "email": "procurement@tnplkarur.in",
        "role": "industry_admin",
        "industry": {
            "id": "f1000000-0000-0000-0000-000000000002",
            "name": "TNPL Karur Paper Plant",
            "verification_status": "approved"
        }
    }
    app.dependency_overrides[get_current_user] = lambda: user_industry_b

    # Industry B attempts to access Industry A's private document
    response = client.get("/api/v1/industries/f1000000-0000-0000-0000-000000000001/documents/b0000000-0000-0000-0000-000000000001/download-url")
    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert "Tenant isolation violation" in response.json()["error"]["message"]

def test_admin_can_access_any_industrys_documents(s3_setup):
    """
    Verifies that Platform Admin CAN access Industry A's document for verification review.
    """
    admin_user = {
        "id": "c1000000-0000-0000-0000-000000000000",
        "email": "admin@waste-exchange.gov",
        "role": "admin",
        "aal": "aal2"
    }
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = client.get("/api/v1/industries/f1000000-0000-0000-0000-000000000001/documents/b0000000-0000-0000-0000-000000000001/download-url")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "presigned_url" in response.json()["data"]
