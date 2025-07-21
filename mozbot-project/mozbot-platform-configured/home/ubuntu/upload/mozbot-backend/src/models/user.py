from src.models import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
import bcrypt

class User(BaseModel):
    __tablename__ = 'users'
    
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    tenants = db.relationship('UserTenant', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_tokens(self):
        """Generate JWT access and refresh tokens"""
        access_token = create_access_token(identity=self.id)
        refresh_token = create_refresh_token(identity=self.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    def get_tenant_role(self, tenant_id):
        """Get user's role in a specific tenant"""
        user_tenant = next((ut for ut in self.tenants if ut.tenant_id == tenant_id), None)
        return user_tenant.role if user_tenant else None
    
    def has_tenant_access(self, tenant_id):
        """Check if user has access to a specific tenant"""
        return any(ut.tenant_id == tenant_id for ut in self.tenants)
    
    def to_dict(self, include_tenants=False):
        data = super().to_dict()
        data.pop('password_hash', None)  # Never include password hash
        
        if include_tenants:
            data['tenants'] = [
                {
                    'id': ut.tenant_id,
                    'name': ut.tenant.name,
                    'role': ut.role,
                    'permissions': ut.permissions
                }
                for ut in self.tenants
            ]
        
        return data
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def create_user(cls, email, password, first_name=None, last_name=None):
        """Create a new user"""
        user = cls(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        return user.save()

