import re
import os
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings

# Password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SUPABASE_JWT_SECRET, algorithm=ALGORITHM)

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and verifies a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[ALGORITHM],
            options={"verify_aud": False}
        )
        return payload
    except JWTError:
        return None

def compute_sha256(data: bytes) -> str:
    """Computes SHA-256 hexadecimal string of raw bytes."""
    return hashlib.sha256(data).hexdigest()

def encrypt_document_aes_gcm(plaintext: bytes) -> bytes:
    """Encrypts document bytes with AES-256-GCM."""
    key_bytes = bytes.fromhex(settings.AES_ENCRYPTION_KEY[:64])
    aesgcm = AESGCM(key_bytes)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext

def decrypt_document_aes_gcm(encrypted_data: bytes) -> bytes:
    """Decrypts document bytes with AES-256-GCM."""
    key_bytes = bytes.fromhex(settings.AES_ENCRYPTION_KEY[:64])
    aesgcm = AESGCM(key_bytes)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)

PHONE_REGEX = re.compile(r'(\+?91[\-\s]?)?[6-9]\d{9}')
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

def mask_chat_message(text: str) -> str:
    """Masks mobile numbers and email addresses in pre-agreement negotiations."""
    masked = PHONE_REGEX.sub('[CONTACT NUMBER REDACTED UNTIL DEAL AGREED]', text)
    masked = EMAIL_REGEX.sub('[EMAIL REDACTED UNTIL DEAL AGREED]', masked)
    return masked

def mask_contact_info(phone: str, email: str) -> tuple[str, str]:
    """Masks phone and email for public / unverified views."""
    masked_phone = phone[:6] + "*****" + phone[-2:] if len(phone) >= 8 else "*****"
    parts = email.split('@')
    if len(parts) == 2:
        masked_email = parts[0][:2] + "***@" + parts[1]
    else:
        masked_email = "*****"
    return masked_phone, masked_email
