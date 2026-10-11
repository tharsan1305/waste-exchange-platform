import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.orm import relationship
from app.core.database import Base

# PostgreSQL domain enum definitions
user_role_enum = ENUM('admin', 'industry_admin', 'industry_staff', name='user_role', create_type=False)
verification_status_enum = ENUM('pending', 'approved', 'rejected', 'suspended', name='verification_status', create_type=False)
industry_doc_type_enum = ENUM('gst', 'license', 'pcb_auth', 'other', name='industry_doc_type', create_type=False)
waste_unit_enum = ENUM('kg', 'ton', name='waste_unit', create_type=False)
recurrence_type_enum = ENUM('weekly', 'monthly', 'quarterly', name='recurrence_type', create_type=False)
listing_status_enum = ENUM('available', 'reserved', 'sold', 'expired', 'removed', 'flagged', name='listing_status', create_type=False)
listing_doc_type_enum = ENUM('lab_report', 'manifest', 'other', name='listing_doc_type', create_type=False)
request_status_enum = ENUM('open', 'accepted', 'rejected', 'withdrawn', name='request_status', create_type=False)
rfq_status_enum = ENUM('open', 'closed', 'awarded', name='rfq_status', create_type=False)
rfq_quote_status_enum = ENUM('submitted', 'accepted', 'rejected', name='rfq_quote_status', create_type=False)
deal_stage_enum = ENUM('negotiation', 'agreed', 'payment_confirmed', 'pickup_scheduled', 'delivered', 'completed', 'cancelled', 'disputed', name='deal_stage', create_type=False)
payment_status_enum = ENUM('pending', 'paid', 'disputed', name='payment_status', create_type=False)
notification_channel_enum = ENUM('in_app', 'email', 'sms', name='notification_channel', create_type=False)
notification_status_enum = ENUM('queued', 'sent', 'failed', name='notification_status', create_type=False)
sentiment_label_enum = ENUM('positive', 'neutral', 'negative', name='sentiment_label', create_type=False)
complaint_type_enum = ENUM('wrong_waste', 'payment_issue', 'fake_listing', 'other', name='complaint_type', create_type=False)
complaint_status_enum = ENUM('open', 'in_review', 'resolved', 'rejected', name='complaint_status', create_type=False)
feedback_type_enum = ENUM('bug', 'suggestion', 'other', name='feedback_type', create_type=False)
fraud_severity_enum = ENUM('low', 'medium', 'high', 'critical', name='fraud_severity', create_type=False)
fraud_status_enum = ENUM('open', 'dismissed', 'confirmed', name='fraud_status', create_type=False)

class User(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(user_role_enum, nullable=False, default="industry_admin")
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="SET NULL"), nullable=True)
    preferred_language = Column(String(10), nullable=False, default="en")
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    industry = relationship("Industry", back_populates="users", foreign_keys=[industry_id])

class Industry(Base):
    __tablename__ = "industries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    gst_number = Column(String(15), unique=True, nullable=False)
    license_number = Column(String(100), nullable=True)
    industry_type = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False, default="Tamil Nadu")
    pincode = Column(String(10), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    contact_email = Column(String(191), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    verification_status = Column(verification_status_enum, nullable=False, default="pending")
    verified_by = Column(UUID(as_uuid=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    trust_score = Column(Float, nullable=False, default=5.00)
    pcb_authorization_no = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="industry", foreign_keys=[User.industry_id])
    listings = relationship("WasteListing", back_populates="industry", cascade="all, delete-orphan")
    documents = relationship("IndustryDocument", back_populates="industry", cascade="all, delete-orphan")

class IndustryDocument(Base):
    __tablename__ = "industry_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    doc_type = Column(industry_doc_type_enum, nullable=False)
    s3_bucket = Column(String(100), nullable=False)
    s3_key = Column(String(255), nullable=False)
    storage_path = Column(Text, nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    status = Column(String(20), nullable=False, default="active")
    uploaded_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    industry = relationship("Industry", back_populates="documents")

class WasteCategory(Base):
    __tablename__ = "waste_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    waste_types = relationship("WasteType", back_populates="category")

class WasteType(Base):
    __tablename__ = "waste_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("waste_categories.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    is_hazardous_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    category = relationship("WasteCategory", back_populates="waste_types")
    listings = relationship("WasteListing", back_populates="waste_type")

class WasteListing(Base):
    __tablename__ = "waste_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    waste_type_id = Column(UUID(as_uuid=True), ForeignKey("waste_types.id", ondelete="RESTRICT"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(waste_unit_enum, nullable=False, default="ton")
    price_per_unit = Column(Float, nullable=False, default=0.0)
    currency = Column(String(10), nullable=False, default="INR")
    is_hazardous = Column(Boolean, default=False)
    hazard_class = Column(String(100), nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurrence = Column(recurrence_type_enum, nullable=True)
    available_from = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(listing_status_enum, nullable=False, default="available")
    batch_code = Column(String(100), unique=True, nullable=False)
    qr_path = Column(String(255), nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    quality_params = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    industry = relationship("Industry", back_populates="listings")
    waste_type = relationship("WasteType", back_populates="listings")
    requests = relationship("Request", back_populates="listing", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="listing")

class Request(Base):
    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("waste_listings.id", ondelete="CASCADE"), nullable=False)
    buyer_industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False)
    offered_price = Column(Float, nullable=False)
    message = Column(Text, nullable=True)
    status = Column(request_status_enum, nullable=False, default="open")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    listing = relationship("WasteListing", back_populates="requests")

class Deal(Base):
    __tablename__ = "deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("waste_listings.id", ondelete="SET NULL"), nullable=True)
    seller_industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="RESTRICT"), nullable=False)
    buyer_industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Float, nullable=False)
    agreed_price_per_unit = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    stage = Column(deal_stage_enum, nullable=False, default="negotiation")
    payment_status = Column(payment_status_enum, nullable=False, default="pending")
    vehicle_number = Column(String(50), nullable=True)
    transporter_name = Column(String(100), nullable=True)
    transporter_pcb_auth_no = Column(String(100), nullable=True)
    pickup_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    co2_saved_kg = Column(Float, nullable=False, default=0.0)
    landfill_diverted_kg = Column(Float, nullable=False, default=0.0)
    money_saved = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    listing = relationship("WasteListing", back_populates="deals")
    reviews = relationship("Review", back_populates="deal")
    manifest = relationship("Manifest", back_populates="deal", uselist=False)

class Manifest(Base):
    __tablename__ = "manifests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), unique=True, nullable=False)
    s3_bucket = Column(String(100), nullable=False)
    s3_key = Column(String(255), nullable=False)
    pdf_path = Column(Text, nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    deal = relationship("Deal", back_populates="manifest")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=True)
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE"), nullable=True)
    sender_industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    sender_user_id = Column(UUID(as_uuid=True), nullable=True)
    body = Column(Text, nullable=False)
    quote_price = Column(Float, nullable=True)
    quote_quantity = Column(Float, nullable=True)
    is_quote = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(150), nullable=False)
    body = Column(Text, nullable=False)
    channel = Column(notification_channel_enum, nullable=False, default="in_app")
    status = Column(notification_status_enum, nullable=False, default="queued")
    read_at = Column(DateTime(timezone=True), nullable=True)
    payload = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    reviewer_industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    reviewee_industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    quality = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    on_time_delivery = Column(Integer, nullable=False)
    communication = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    sentiment = Column(sentiment_label_enum, nullable=False, default="positive")
    sentiment_score = Column(Float, nullable=False, default=0.85)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    deal = relationship("Deal", back_populates="reviews")
    __table_args__ = (UniqueConstraint("deal_id", "reviewer_industry_id", name="uq_deal_reviewer"),)

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="SET NULL"), nullable=True)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("waste_listings.id", ondelete="SET NULL"), nullable=True)
    raised_by_industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    against_industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    type = Column(complaint_type_enum, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(complaint_status_enum, nullable=False, default="open")
    resolution_note = Column(Text, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class PlatformFeedback(Base):
    __tablename__ = "platform_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    type = Column(feedback_type_enum, nullable=False, default="suggestion")
    message = Column(Text, nullable=False)
    sentiment = Column(sentiment_label_enum, nullable=False, default="neutral")
    status = Column(String(20), nullable=False, default="new")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_user_id = Column(UUID(as_uuid=True), nullable=True)
    actor_role = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    before = Column(JSONB, nullable=True)
    after = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
