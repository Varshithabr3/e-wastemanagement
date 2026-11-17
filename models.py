from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, 
    Boolean, Numeric, ForeignKey, Table, Enum
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Junction Table for CollectionRequest <-> EwasteItem
collection_request_items = Table(
    'collection_request_items',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('request_id', Integer, ForeignKey('collection_requests.id', ondelete='CASCADE'), nullable=False),
    Column('item_id', Integer, ForeignKey('ewaste_items.id', ondelete='CASCADE'), nullable=False)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone = Column(String(25), nullable=False)
    password_hash = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), default='Bengaluru')
    pincode = Column(String(15), nullable=True)
    reset_token = Column(String(100), nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationships
    ewaste_items = relationship('EwasteItem', back_populates='user', cascade='all, delete-orphan')
    collection_requests = relationship('CollectionRequest', back_populates='user', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'pincode': self.pincode,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }

class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='Super Administrator', nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role
        }

class EwasteItem(Base):
    __tablename__ = 'ewaste_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category = Column(String(80), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    item_condition = Column(String(50), default='Not Working', nullable=False)  # Working, Damaged, Not Working
    description = Column(Text, nullable=True)
    location = Column(String(150), nullable=False)
    image_filename = Column(String(255), nullable=True)
    status = Column(String(50), default='Available', nullable=False, index=True)  # Available, In Request, Collected, Recycled
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationships
    user = relationship('User', back_populates='ewaste_items')
    requests = relationship('CollectionRequest', secondary=collection_request_items, back_populates='items')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'item_condition': self.item_condition,
            'description': self.description or '',
            'location': self.location,
            'image_filename': self.image_filename,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }

class CollectionRequest(Base):
    __tablename__ = 'collection_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_code = Column(String(40), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    pickup_address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    pincode = Column(String(15), nullable=False)
    preferred_date = Column(Date, nullable=False)
    preference_type = Column(String(50), default='Doorstep Pickup', nullable=False)  # Doorstep Pickup, Centre Drop-Off
    status = Column(String(50), default='Pending', nullable=False, index=True)  # Pending, Approved, In Progress, Completed, Rejected
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    user = relationship('User', back_populates='collection_requests')
    items = relationship('EwasteItem', secondary=collection_request_items, back_populates='requests')

    def to_dict(self):
        return {
            'id': self.id,
            'request_code': self.request_code,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else 'Unknown',
            'user_email': self.user.email if self.user else '',
            'user_phone': self.user.phone if self.user else '',
            'pickup_address': self.pickup_address,
            'city': self.city,
            'pincode': self.pincode,
            'preferred_date': self.preferred_date.strftime('%Y-%m-%d') if self.preferred_date else '',
            'preference_type': self.preference_type,
            'status': self.status,
            'admin_notes': self.admin_notes or '',
            'item_count': len(self.items),
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else ''
        }

class RecyclingCentre(Base):
    __tablename__ = 'recycling_centres'

    id = Column(Integer, primary_key=True, autoincrement=True)
    centre_name = Column(String(220), nullable=False)
    complete_address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True, index=True)
    pincode = Column(String(15), nullable=True, index=True)
    state = Column(String(100), default='Karnataka', nullable=False)
    facility_type = Column(String(80), default='Authorized Recycler', nullable=False) # Authorized Recycler, Authorized Dismantler, Collection Centre, Authorized Refurbisher
    contact_phone = Column(String(60), nullable=True)
    contact_email = Column(String(120), nullable=True)
    website_url = Column(String(255), nullable=True)
    services_offered = Column(Text, nullable=True)
    accepted_categories = Column(Text, nullable=False)  # e.g. "Mobile Phones, Laptops, Batteries"
    source_url = Column(Text, nullable=False)
    last_verified_date = Column(Date, nullable=False)
    is_official_verified = Column(Boolean, default=True, nullable=False, index=True)
    directions_url = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'centre_name': self.centre_name,
            'complete_address': self.complete_address,
            'city': self.city,
            'district': self.district or 'Bengaluru Urban',
            'pincode': self.pincode or 'N/A',
            'state': self.state,
            'facility_type': self.facility_type,
            'contact_phone': self.contact_phone if (self.contact_phone and self.contact_phone.strip() != 'N/A') else 'Contact details not available',
            'contact_email': self.contact_email if (self.contact_email and self.contact_email.strip() != 'N/A') else 'Contact details not available',
            'website_url': self.website_url if (self.website_url and self.website_url != '#') else None,
            'services_offered': self.services_offered or '',
            'accepted_categories': self.accepted_categories,
            'source_url': self.source_url,
            'last_verified_date': self.last_verified_date.strftime('%Y-%m-%d') if self.last_verified_date else '',
            'is_official_verified': bool(self.is_official_verified),
            'directions_url': self.directions_url if (self.directions_url and self.directions_url.startswith('http')) else None,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None
        }

class DisposalGuideline(Base):
    __tablename__ = 'disposal_guidelines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), unique=True, nullable=False)
    title = Column(String(220), nullable=False)
    summary = Column(Text, nullable=False)
    step_by_step = Column(Text, nullable=False)
    dos_and_donts = Column(Text, nullable=False)
    hazards_prevented = Column(Text, nullable=True)
    icon_class = Column(String(80), default='fa-recycle', nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'title': self.title,
            'summary': self.summary,
            'step_by_step': self.step_by_step,
            'dos_and_donts': self.dos_and_donts,
            'hazards_prevented': self.hazards_prevented or '',
            'icon_class': self.icon_class
        }

class AwarenessContent(Base):
    __tablename__ = 'awareness_content'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(220), nullable=False)
    category = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    toxic_substance = Column(String(120), nullable=True)
    health_hazard = Column(Text, nullable=True)
    environmental_hazard = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'summary': self.summary,
            'content': self.content,
            'toxic_substance': self.toxic_substance or 'General E-Waste',
            'health_hazard': self.health_hazard or '',
            'environmental_hazard': self.environmental_hazard or ''
        }
