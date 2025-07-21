from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from src.models.user import User
from src.models.tenant import Tenant, UserTenant
from src.models import db
from src.utils.auth import validate_json
from src.utils.responses import success_response, error_response, validation_error_response, conflict_response
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, None

@auth_bp.route('/register', methods=['POST'])
@validate_json('email', 'password', 'first_name', 'last_name', 'tenant_name')
def register():
    """Register a new user and create their tenant"""
    data = request.json
    
    # Validate input
    errors = []
    
    if not validate_email(data['email']):
        errors.append({'field': 'email', 'message': 'Invalid email format'})
    
    is_valid_password, password_error = validate_password(data['password'])
    if not is_valid_password:
        errors.append({'field': 'password', 'message': password_error})
    
    if len(data['tenant_name'].strip()) < 2:
        errors.append({'field': 'tenant_name', 'message': 'Tenant name must be at least 2 characters'})
    
    if errors:
        return validation_error_response(errors)
    
    # Check if user already exists
    if User.find_by_email(data['email']):
        return conflict_response('User with this email already exists')
    
    # Generate subdomain from tenant name
    subdomain = re.sub(r'[^a-zA-Z0-9]', '', data['tenant_name'].lower())[:20]
    if len(subdomain) < 3:
        subdomain = f"tenant{User.query.count() + 1}"
    
    # Check if subdomain is taken
    counter = 1
    original_subdomain = subdomain
    while Tenant.query.filter_by(subdomain=subdomain).first():
        subdomain = f"{original_subdomain}{counter}"
        counter += 1
    
    try:
        # Create user
        user = User.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        
        # Create tenant
        tenant = Tenant(
            name=data['tenant_name'],
            subdomain=subdomain,
            plan_type='basic',
            status='active'
        )
        tenant.save()
        
        # Associate user with tenant as owner
        user_tenant = UserTenant(
            user_id=user.id,
            tenant_id=tenant.id,
            role='owner'
        )
        user_tenant.save()
        
        # Generate tokens
        tokens = user.generate_tokens()
        
        return success_response({
            'user': user.to_dict(include_tenants=True),
            'tenant': tenant.to_dict(),
            **tokens
        }, status_code=201)
        
    except Exception as e:
        db.session.rollback()
        return error_response('Registration failed', status_code=500)

@auth_bp.route('/login', methods=['POST'])
@validate_json('email', 'password')
def login():
    """Authenticate user and return tokens"""
    data = request.json
    
    user = User.find_by_email(data['email'])
    
    if not user or not user.check_password(data['password']):
        return error_response('Invalid email or password', status_code=401)
    
    if not user.is_active:
        return error_response('Account is deactivated', status_code=401)
    
    tokens = user.generate_tokens()
    
    return success_response({
        'user': user.to_dict(include_tenants=True),
        **tokens
    })

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return error_response('User not found or inactive', status_code=401)
    
    access_token = create_access_token(identity=user.id)
    
    return success_response({
        'access_token': access_token
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return error_response('User not found', status_code=404)
    
    return success_response({
        'user': user.to_dict(include_tenants=True)
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard tokens)"""
    return success_response({'message': 'Successfully logged out'})

@auth_bp.route('/forgot-password', methods=['POST'])
@validate_json('email')
def forgot_password():
    """Request password reset (placeholder implementation)"""
    data = request.json
    
    user = User.find_by_email(data['email'])
    
    # Always return success for security (don't reveal if email exists)
    return success_response({
        'message': 'If an account with this email exists, a password reset link has been sent'
    })

@auth_bp.route('/reset-password', methods=['POST'])
@validate_json('token', 'password')
def reset_password():
    """Reset password with token (placeholder implementation)"""
    data = request.json
    
    # TODO: Implement token validation and password reset
    return success_response({
        'message': 'Password has been reset successfully'
    })

