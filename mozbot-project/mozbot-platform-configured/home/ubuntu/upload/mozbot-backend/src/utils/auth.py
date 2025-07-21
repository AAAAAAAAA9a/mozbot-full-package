from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User
from src.models.tenant import Tenant

def auth_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_active:
            return jsonify({'success': False, 'error': {'message': 'User not found or inactive'}}), 401
        
        g.current_user = current_user
        return f(*args, **kwargs)
    
    return decorated_function

def tenant_required(f):
    """Decorator to require tenant access"""
    @wraps(f)
    @auth_required
    def decorated_function(*args, **kwargs):
        # Get tenant_id from URL parameters or request body
        tenant_id = kwargs.get('tenant_id') or request.json.get('tenant_id') if request.json else None
        
        if not tenant_id:
            return jsonify({'success': False, 'error': {'message': 'Tenant ID required'}}), 400
        
        # Check if user has access to this tenant
        if not g.current_user.has_tenant_access(tenant_id):
            return jsonify({'success': False, 'error': {'message': 'Access denied to this tenant'}}), 403
        
        # Get tenant and add to context
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'success': False, 'error': {'message': 'Tenant not found'}}), 404
        
        g.current_tenant = tenant
        g.current_user_role = g.current_user.get_tenant_role(tenant_id)
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin role in tenant"""
    @wraps(f)
    @tenant_required
    def decorated_function(*args, **kwargs):
        if g.current_user_role not in ['admin', 'owner']:
            return jsonify({'success': False, 'error': {'message': 'Admin access required'}}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_json(*required_fields):
    """Decorator to validate required JSON fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.json:
                return jsonify({'success': False, 'error': {'message': 'JSON data required'}}), 400
            
            missing_fields = []
            for field in required_fields:
                if field not in request.json:
                    missing_fields.append(field)
            
            if missing_fields:
                return jsonify({
                    'success': False, 
                    'error': {
                        'message': 'Missing required fields',
                        'details': [{'field': field, 'message': f'{field} is required'} for field in missing_fields]
                    }
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def paginate_query(query, page=1, per_page=20, max_per_page=100):
    """Paginate a SQLAlchemy query"""
    if per_page > max_per_page:
        per_page = max_per_page
    
    paginated = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': [item.to_dict() for item in paginated.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
    }

