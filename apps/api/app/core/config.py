from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = Field(default="development")
    PORT: int = Field(default=8000)
    ALLOWED_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:3000")

    # Supabase credentials
    SUPABASE_URL: str = Field(default="https://mock.supabase.co")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="mock-service-role-key")
    SUPABASE_JWT_SECRET: str = Field(default="mock-jwt-secret-for-development-mode-testing-32b")

    # AWS S3 Storage Credentials (Hackathon Priority)
    AWS_ACCESS_KEY_ID: str = Field(default="mock-aws-access-key")
    AWS_SECRET_ACCESS_KEY: str = Field(default="mock-aws-secret-key")
    AWS_REGION: str = Field(default="ap-south-1")
    S3_BUCKET: str = Field(default="waste-exchange-private-storage")

    # Cryptography & Local AES
    AES_ENCRYPTION_KEY: str = Field(default="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")

    # Security & Rate Limiting
    RATE_LIMIT_LOGIN: str = Field(default="5/minute")
    RATE_LIMIT_DEFAULT: str = Field(default="60/minute")
    ENABLE_CLAMAV_SCAN: bool = Field(default=False)
    CLAMAV_HOST: str = Field(default="localhost")
    CLAMAV_PORT: int = Field(default=3310)

    # Logistics Defaults
    OSRM_ENDPOINT: str = Field(default="https://router.project-osrm.org")
    PER_KM_TON_RATE: float = Field(default=4.50)
    BASE_TRANSPORT_FARE: float = Field(default=1200.00)

    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

settings = Settings()
