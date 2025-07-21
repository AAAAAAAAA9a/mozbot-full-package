from flask import Blueprint, request, g
from src.models.chatbot import Chatbot, ChatbotChannel, KnowledgeArticle, FAQ
from src.models import db
from src.utils.auth import tenant_required, admin_required, validate_json
from src.utils.responses import success_response, error_response, not_found_response, validation_error_response
from src.utils.auth import paginate_query

chatbots_bp = Blueprint('chatbots', __name__)

@chatbots_bp.route('', methods=['GET'])
@tenant_required
def list_chatbots():
    """List all chatbots for the current tenant"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Chatbot.query.filter_by(tenant_id=g.current_tenant.id)
    
    result = paginate_query(query, page, per_page)
    
    # Add stats to each chatbot
    for chatbot_data in result['items']:
        chatbot = Chatbot.query.get(chatbot_data['id'])
        chatbot_data.update(chatbot.to_dict(include_stats=True))
    
    return success_response(result)

@chatbots_bp.route('', methods=['POST'])
@admin_required
@validate_json('name')
def create_chatbot():
    """Create a new chatbot"""
    data = request.json
    
    # Validate input
    errors = []
    if len(data['name'].strip()) < 2:
        errors.append({'field': 'name', 'message': 'Name must be at least 2 characters'})
    
    if errors:
        return validation_error_response(errors)
    
    try:
        chatbot = Chatbot(
            tenant_id=g.current_tenant.id,
            name=data['name'],
            description=data.get('description', ''),
            widget_settings=data.get('widget_settings', {}),
            ai_settings=data.get('ai_settings', {}),
            branding=data.get('branding', {})
        )
        chatbot.save()
        
        # Create default web channel
        web_channel = ChatbotChannel(
            tenant_id=g.current_tenant.id,
            chatbot_id=chatbot.id,
            channel_type='web',
            channel_config={},
            is_active=True
        )
        web_channel.save()
        
        return success_response(chatbot.to_dict(), status_code=201)
        
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to create chatbot', status_code=500)

@chatbots_bp.route('/<chatbot_id>', methods=['GET'])
@tenant_required
def get_chatbot(chatbot_id):
    """Get chatbot details"""
    chatbot = Chatbot.query.filter_by(
        id=chatbot_id,
        tenant_id=g.current_tenant.id
    ).first()
    
    if not chatbot:
        return not_found_response('Chatbot')
    
    return success_response(chatbot.to_dict(include_stats=True))

@chatbots_bp.route('/<chatbot_id>', methods=['PUT'])
@admin_required
def update_chatbot(chatbot_id):
    """Update chatbot"""
    chatbot = Chatbot.query.filter_by(
        id=chatbot_id,
        tenant_id=g.current_tenant.id
    ).first()
    
    if not chatbot:
        return not_found_response('Chatbot')
    
    data = request.json or {}
    
    # Update fields
    if 'name' in data:
        if len(data['name'].strip()) < 2:
            return validation_error_response([{'field': 'name', 'message': 'Name must be at least 2 characters'}])
        chatbot.name = data['name']
    
    if 'description' in data:
        chatbot.description = data['description']
    
    if 'widget_settings' in data:
        chatbot.widget_settings = data['widget_settings']
    
    if 'ai_settings' in data:
        chatbot.ai_settings = data['ai_settings']
    
    if 'branding' in data:
        chatbot.branding = data['branding']
    
    try:
        chatbot.save()
        return success_response(chatbot.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to update chatbot', status_code=500)

@chatbots_bp.route('/<chatbot_id>', methods=['DELETE'])
@admin_required
def delete_chatbot(chatbot_id):
    """Delete chatbot"""
    chatbot = Chatbot.query.filter_by(
        id=chatbot_id,
        tenant_id=g.current_tenant.id
    ).first()
    
    if not chatbot:
        return not_found_response('Chatbot')
    
    try:
        chatbot.delete()
        return success_response({'message': 'Chatbot deleted successfully'}, status_code=204)
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to delete chatbot', status_code=500)

@chatbots_bp.route('/<chatbot_id>/status', methods=['PATCH'])
@admin_required
def toggle_chatbot_status(chatbot_id):
    """Toggle chatbot active status"""
    chatbot = Chatbot.query.filter_by(
        id=chatbot_id,
        tenant_id=g.current_tenant.id
    ).first()
    
    if not chatbot:
        return not_found_response('Chatbot')
    
    chatbot.is_active = not chatbot.is_active
    
    try:
        chatbot.save()
        return success_response({
            'is_active': chatbot.is_active,
            'message': f"Chatbot {'activated' if chatbot.is_active else 'deactivated'}"
        })
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to update chatbot status', status_code=500)

# Channels endpoints
@chatbots_bp.route('/<chatbot_id>/channels', methods=['GET'])
@tenant_required
def list_chatbot_channels(chatbot_id):
    """List chatbot channels"""
    chatbot = Chatbot.query.filter_by(
        id=chatbot_id,
        tenant_id=g.current_tenant.id
    ).first()
    
    if not chatbot:
        return not_found_response('Chatbot')
    
    channels = ChatbotChannel.query.filter_by(
        chatbot_id=chatbot_id,
        tenant_id=g.current_tenant.id
    ).all()
    
    return success_response([channel.to_dict() for channel in channels])

@chatbots_bp.route('/<chatbot_id>/channels', methods=['POST'])
@admin_required
@validate_json('channel_type')
def create_chatbot_channel(chatbot_id):
    """Add new channel to chatbot"""
    chatbot = Chatbot.query.filter_by(
        id=chatbot_id,
        tenant_id=g.current_tenant.id
    ).first()
    
    if not chatbot:
        return not_found_response('Chatbot')
    
    data = request.json
    
    # Validate channel type
    valid_channels = ['web', 'telegram', 'whatsapp', 'messenger']
    if data['channel_type'] not in valid_channels:
        return validation_error_response([{
            'field': 'channel_type',
            'message': f"Channel type must be one of: {', '.join(valid_channels)}"
        }])
    
    # Check if channel already exists
    existing_channel = ChatbotChannel.query.filter_by(
        chatbot_id=chatbot_id,
        channel_type=data['channel_type'],
        tenant_id=g.current_tenant.id
    ).first()
    
    if existing_channel:
        return error_response(f"{data['channel_type'].title()} channel already exists for this chatbot", status_code=409)
    
    try:
        channel = ChatbotChannel(
            tenant_id=g.current_tenant.id,
            chatbot_id=chatbot_id,
            channel_type=data['channel_type'],
            channel_config=data.get('channel_config', {}),
            is_active=data.get('is_active', True)
        )
        channel.save()
        
        return success_response(channel.to_dict(), status_code=201)
        
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to create channel', status_code=500)

# Widget configuration endpoints
@chatbots_bp.route('/<chatbot_id>/widget-config', methods=['GET'])
@tenant_required
def get_widget_config(chatbot_id):
    """Get widget configuration"""
    chatbot = Chatbot.query.filter_by(
        id=chatbot_id,
        tenant_id=g.current_tenant.id
    ).first()
    
    if not chatbot:
        return not_found_response('Chatbot')
    
    return success_response({
        'widget_settings': chatbot.widget_settings,
        'branding': chatbot.branding,
        'is_active': chatbot.is_active
    })

@chatbots_bp.route('/<chatbot_id>/widget-config', methods=['PUT'])
@admin_required
def update_widget_config(chatbot_id):
    """Update widget configuration"""
    chatbot = Chatbot.query.filter_by(
        id=chatbot_id,
        tenant_id=g.current_tenant.id
    ).first()
    
    if not chatbot:
        return not_found_response('Chatbot')
    
    data = request.json or {}
    
    if 'widget_settings' in data:
        chatbot.widget_settings = data['widget_settings']
    
    if 'branding' in data:
        chatbot.branding = data['branding']
    
    try:
        chatbot.save()
        return success_response({
            'widget_settings': chatbot.widget_settings,
            'branding': chatbot.branding
        })
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to update widget configuration', status_code=500)

