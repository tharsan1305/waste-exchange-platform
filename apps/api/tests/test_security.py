from app.core.security import (
    compute_sha256,
    encrypt_document_aes_gcm,
    decrypt_document_aes_gcm,
    mask_chat_message,
    mask_contact_info
)

def test_aes_gcm_document_encryption():
    secret_data = b"CONFIDENTIAL INDUSTRIAL LAB REPORT - 2026"
    encrypted = encrypt_document_aes_gcm(secret_data)
    assert encrypted != secret_data

    decrypted = decrypt_document_aes_gcm(encrypted)
    assert decrypted == secret_data

def test_sha256_fingerprint():
    data = b"Hello Industrial Symbiosis"
    sha = compute_sha256(data)
    assert len(sha) == 64
    assert sha == compute_sha256(data)

def test_chat_message_contact_masking():
    # Attempting to leak phone number
    msg_with_phone = "Hello, please call our GM directly at 9840123456 to fix price."
    masked = mask_chat_message(msg_with_phone)
    assert "9840123456" not in masked
    assert "[CONTACT NUMBER REDACTED UNTIL DEAL AGREED]" in masked

    # Attempting to leak email
    msg_with_email = "Write to ops@factory.com for offline quote."
    masked_email = mask_chat_message(msg_with_email)
    assert "ops@factory.com" not in masked_email
    assert "[EMAIL REDACTED UNTIL DEAL AGREED]" in masked_email

def test_contact_info_masking():
    phone, email = mask_contact_info("+91 9840123456", "procurement@tnpl.in")
    assert "pr***@tnpl.in" == email
    assert "*****" in phone
