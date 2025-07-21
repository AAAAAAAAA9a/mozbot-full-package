from flask import jsonify

def success_response(data=None, message=None, status_code=200):
    """Create a successful response"""
    response = {'success': True}
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return jsonify(response), status_code

def error_response(message, details=None, code=None, status_code=400):
    """Create an error response"""
    error = {'message': message}
    
    if details:
        error['details'] = details
    
    if code:
        error['code'] = code
    
    response = {
        'success': False,
        'error': error
    }
    
    return jsonify(response), status_code

def validation_error_response(errors):
    """Create a validation error response"""
    return error_response(
        message='Validation failed',
        details=errors,
        code='VALIDATION_ERROR',
        status_code=422
    )

def not_found_response(resource='Resource'):
    """Create a not found response"""
    return error_response(
        message=f'{resource} not found',
        code='NOT_FOUND',
        status_code=404
    )

def unauthorized_response(message='Authentication required'):
    """Create an unauthorized response"""
    return error_response(
        message=message,
        code='UNAUTHORIZED',
        status_code=401
    )

def forbidden_response(message='Access denied'):
    """Create a forbidden response"""
    return error_response(
        message=message,
        code='FORBIDDEN',
        status_code=403
    )

def conflict_response(message='Resource conflict'):
    """Create a conflict response"""
    return error_response(
        message=message,
        code='CONFLICT',
        status_code=409
    )

def server_error_response(message='Internal server error'):
    """Create a server error response"""
    return error_response(
        message=message,
        code='INTERNAL_ERROR',
        status_code=500
    )

