from src.models import db, BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Tenant(BaseModel):
    __tablename__ = 'tenants'
    
    name = db.Column(db.String(255), nullable=False)
    subdomain = db.Column(db.String(100), unique=True, nullable=False)
    plan_type = db.Column(db.String(50), nullable=False, default='basic')
    status = db.Column(db.String(20), nullable=False, default='active')
    settings = db.Column(db.JSON, default={})
    
    # Relationships
    users = db.relationship('UserTenant', back_populates='tenant', cascade='all, delete-orphan')
    chatbots = db.relationship('Chatbot', back_populates='tenant', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tenant {self.name}>'
    
    def to_dict(self):
        data = super().to_dict()
        data['chatbot_count'] = len(self.chatbots) if self.chatbots else 0
        data['user_count'] = len(self.users) if self.users else 0
        return data

class UserTenant(BaseModel):
    __tablename__ = 'user_tenants'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='member')
    permissions = db.Column(db.JSON, default={})
    
    # Relationships
    user = db.relationship('User', back_populates='tenants')
    tenant = db.relationship('Tenant', back_populates='users')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'tenant_id', name='unique_user_tenant'),)
    
    def __repr__(self):
        return f'<UserTenant {self.user_id}:{self.tenant_id}>'

