from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.channel_service import channel_service
from src.models.chatbot import Chatbot
from src.models.conversation import Conversation, Message
from src.utils.auth import tenant_required
from src.utils.responses import success_response, error_response
import json

channels_bp = Blueprint('channels', __name__)

@channels_bp.route('/supported', methods=['GET'])
@jwt_required()
def get_supported_channels():
    """Get list of supported communication channels"""
    try:
        channels = channel_service.get_supported_channels()
        return success_response(channels)
        
    except Exception as e:
        return error_response(f"Failed to fetch supported channels: {str(e)}", 500)

@channels_bp.route('/register', methods=['POST'])
@jwt_required()
@tenant_required
def register_channel():
    """Register a new communication channel for the tenant"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['channel_type', 'config']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        channel_type = data['channel_type']
        config = data['config']
        
        # Register channel
        result = channel_service.register_channel(tenant_id, channel_type, config)
        
        if result['success']:
            return success_response({
                'message': result['message'],
                'channel_type': channel_type
            }, 201)
        else:
            return error_response(result['error'], 400)
        
    except Exception as e:
        return error_response(f"Failed to register channel: {str(e)}", 500)

@channels_bp.route('/test', methods=['POST'])
@jwt_required()
@tenant_required
def test_channel():
    """Test a channel configuration"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['channel_type', 'config']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        channel_type = data['channel_type']
        config = data['config']
        
        # Get adapter class and test configuration
        if channel_type not in channel_service.adapter_classes:
            return error_response(f"Unsupported channel type: {channel_type}", 400)
        
        adapter_class = channel_service.adapter_classes[channel_type]
        adapter = adapter_class(config)
        
        test_result = channel_service.test_channel_config(adapter)
        
        if test_result['success']:
            return success_response({
                'message': 'Channel configuration test successful',
                'channel_type': channel_type
            })
        else:
            return error_response(f"Channel test failed: {test_result['error']}", 400)
        
    except Exception as e:
        return error_response(f"Channel test failed: {str(e)}", 500)

@channels_bp.route('/send', methods=['POST'])
@jwt_required()
@tenant_required
def send_message():
    """Send a message through a specific channel"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['channel_type', 'recipient_id', 'message']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        channel_type = data['channel_type']
        recipient_id = data['recipient_id']
        message = data['message']
        
        # Optional parameters
        kwargs = {}
        if 'reply_markup' in data:
            kwargs['reply_markup'] = data['reply_markup']
        if 'parse_mode' in data:
            kwargs['parse_mode'] = data['parse_mode']
        if 'template' in data:
            kwargs['template'] = data['template']
        
        # Send message
        result = channel_service.send_message(
            tenant_id, 
            channel_type, 
            recipient_id, 
            message, 
            **kwargs
        )
        
        if result['success']:
            return success_response({
                'message': 'Message sent successfully',
                'message_id': result.get('message_id'),
                'channel_type': channel_type
            })
        else:
            return error_response(result['error'], 400)
        
    except Exception as e:
        return error_response(f"Failed to send message: {str(e)}", 500)

@channels_bp.route('/webhook/<channel_type>', methods=['POST'])
def receive_webhook(channel_type):
    """Receive webhook from communication channels"""
    try:
        # Get tenant_id from query parameters or headers
        tenant_id = request.args.get('tenant_id') or request.headers.get('X-Tenant-ID')
        
        if not tenant_id:
            return error_response("Tenant ID required", 400)
        
        tenant_id = int(tenant_id)
        webhook_data = request.get_json()
        
        if not webhook_data:
            return error_response("No webhook data provided", 400)
        
        # Process webhook
        result = channel_service.process_webhook(tenant_id, channel_type, webhook_data)
        
        if result['success']:
            return success_response({
                'message': 'Webhook processed successfully',
                'conversation_id': result.get('conversation_id'),
                'message_id': result.get('message_id')
            })
        else:
            return error_response(result['error'], 400)
        
    except Exception as e:
        return error_response(f"Webhook processing failed: {str(e)}", 500)

@channels_bp.route('/webhook/<channel_type>', methods=['GET'])
def verify_webhook(channel_type):
    """Verify webhook for channels that require it (like Facebook)"""
    try:
        if channel_type in ['messenger', 'whatsapp']:
            # Facebook webhook verification
            verify_token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            # This would check against stored verify token for the tenant
            # For now, just return the challenge
            if verify_token and challenge:
                return challenge
            else:
                return error_response("Invalid verification request", 400)
        
        return error_response(f"Webhook verification not supported for {channel_type}", 400)
        
    except Exception as e:
        return error_response(f"Webhook verification failed: {str(e)}", 500)

@channels_bp.route('/conversations', methods=['GET'])
@jwt_required()
@tenant_required
def get_conversations():
    """Get conversations across all channels"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        
        # Query parameters
        channel_type = request.args.get('channel_type')
        status = request.args.get('status', 'active')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Build query
        query = Conversation.query.filter_by(tenant_id=tenant_id)
        
        if channel_type:
            query = query.filter_by(channel_type=channel_type)
        
        if status:
            query = query.filter_by(status=status)
        
        # Paginate
        conversations = query.order_by(Conversation.updated_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        conversations_data = []
        for conversation in conversations.items:
            # Get latest message
            latest_message = Message.query.filter_by(
                conversation_id=conversation.id
            ).order_by(Message.created_at.desc()).first()
            
            conversations_data.append({
                'id': conversation.id,
                'user_id': conversation.user_id,
                'user_name': conversation.user_name,
                'user_email': conversation.user_email,
                'channel_type': conversation.channel_type,
                'status': conversation.status,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'latest_message': {
                    'content': latest_message.content if latest_message else None,
                    'sender_type': latest_message.sender_type if latest_message else None,
                    'created_at': latest_message.created_at.isoformat() if latest_message else None
                } if latest_message else None,
                'message_count': Message.query.filter_by(conversation_id=conversation.id).count()
            })
        
        return success_response({
            'conversations': conversations_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': conversations.total,
                'pages': conversations.pages,
                'has_next': conversations.has_next,
                'has_prev': conversations.has_prev
            }
        })
        
    except Exception as e:
        return error_response(f"Failed to fetch conversations: {str(e)}", 500)

@channels_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
@tenant_required
def get_conversation_messages(conversation_id):
    """Get messages for a specific conversation"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        
        # Verify conversation belongs to tenant
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            tenant_id=tenant_id
        ).first()
        
        if not conversation:
            return error_response("Conversation not found", 404)
        
        # Query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        # Get messages
        messages = Message.query.filter_by(
            conversation_id=conversation_id
        ).order_by(Message.created_at.asc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        messages_data = []
        for message in messages.items:
            messages_data.append({
                'id': message.id,
                'content': message.content,
                'sender_type': message.sender_type,
                'platform_message_id': message.platform_message_id,
                'created_at': message.created_at.isoformat(),
                'meta_data': message.meta_data
            })
        
        return success_response({
            'conversation': {
                'id': conversation.id,
                'user_id': conversation.user_id,
                'user_name': conversation.user_name,
                'channel_type': conversation.channel_type,
                'status': conversation.status
            },
            'messages': messages_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': messages.total,
                'pages': messages.pages,
                'has_next': messages.has_next,
                'has_prev': messages.has_prev
            }
        })
        
    except Exception as e:
        return error_response(f"Failed to fetch messages: {str(e)}", 500)

@channels_bp.route('/conversations/<int:conversation_id>/reply', methods=['POST'])
@jwt_required()
@tenant_required
def reply_to_conversation(conversation_id):
    """Reply to a conversation through its original channel"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        data = request.get_json()
        
        if 'message' not in data:
            return error_response("Message content required", 400)
        
        # Verify conversation belongs to tenant
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            tenant_id=tenant_id
        ).first()
        
        if not conversation:
            return error_response("Conversation not found", 404)
        
        message_content = data['message']
        
        # Send message through the conversation's channel
        result = channel_service.send_message(
            tenant_id,
            conversation.channel_type,
            conversation.user_id,
            message_content
        )
        
        if result['success']:
            # Save the message
            message = Message(
                conversation_id=conversation_id,
                content=message_content,
                sender_type='agent',
                platform_message_id=result.get('message_id'),
                meta_data={
                    'channel_type': conversation.channel_type,
                    'sent_by_user_id': user_id,
                    'platform_response': result.get('platform_response', {})
                }
            )
            message.save()
            
            # Update conversation timestamp
            conversation.updated_at = message.created_at
            conversation.save()
            
            return success_response({
                'message': 'Reply sent successfully',
                'message_id': message.id,
                'platform_message_id': result.get('message_id')
            })
        else:
            return error_response(result['error'], 400)
        
    except Exception as e:
        return error_response(f"Failed to send reply: {str(e)}", 500)

@channels_bp.route('/analytics', methods=['GET'])
@jwt_required()
@tenant_required
def get_channel_analytics():
    """Get analytics data for all channels"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        
        # Query parameters
        days = int(request.args.get('days', 30))
        
        # Get conversation counts by channel
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        channel_stats = Conversation.query.filter(
            and_(
                Conversation.tenant_id == tenant_id,
                Conversation.created_at >= start_date
            )
        ).with_entities(
            Conversation.channel_type,
            func.count(Conversation.id).label('conversation_count')
        ).group_by(Conversation.channel_type).all()
        
        # Get message counts by channel
        message_stats = Message.query.join(Conversation).filter(
            and_(
                Conversation.tenant_id == tenant_id,
                Message.created_at >= start_date
            )
        ).with_entities(
            Conversation.channel_type,
            func.count(Message.id).label('message_count'),
            func.count(func.distinct(Message.conversation_id)).label('active_conversations')
        ).group_by(Conversation.channel_type).all()
        
        # Combine stats
        analytics_data = {}
        
        for stat in channel_stats:
            channel_type = stat.channel_type or 'web'
            analytics_data[channel_type] = {
                'channel_type': channel_type,
                'conversation_count': stat.conversation_count,
                'message_count': 0,
                'active_conversations': 0
            }
        
        for stat in message_stats:
            channel_type = stat.channel_type or 'web'
            if channel_type in analytics_data:
                analytics_data[channel_type]['message_count'] = stat.message_count
                analytics_data[channel_type]['active_conversations'] = stat.active_conversations
        
        # Calculate totals
        total_conversations = sum(data['conversation_count'] for data in analytics_data.values())
        total_messages = sum(data['message_count'] for data in analytics_data.values())
        
        return success_response({
            'period_days': days,
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'channels': list(analytics_data.values()),
            'supported_channels': channel_service.get_supported_channels()
        })
        
    except Exception as e:
        return error_response(f"Failed to fetch analytics: {str(e)}", 500)

@channels_bp.route('/status', methods=['GET'])
@jwt_required()
@tenant_required
def get_channel_status():
    """Get status of all configured channels for the tenant"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        
        # Get all registered channels for this tenant
        registered_channels = []
        
        for channel_type in channel_service.adapter_classes.keys():
            adapter = channel_service.get_adapter(tenant_id, channel_type)
            if adapter:
                registered_channels.append({
                    'channel_type': channel_type,
                    'status': 'active',
                    'config_valid': True
                })
        
        # Get supported but not configured channels
        all_supported = channel_service.get_supported_channels()
        configured_types = [ch['channel_type'] for ch in registered_channels]
        
        available_channels = [
            {
                'channel_type': ch['type'],
                'name': ch['name'],
                'description': ch['description'],
                'status': 'not_configured',
                'required_config': ch['required_config']
            }
            for ch in all_supported
            if ch['type'] not in configured_types
        ]
        
        return success_response({
            'registered_channels': registered_channels,
            'available_channels': available_channels,
            'total_registered': len(registered_channels),
            'total_available': len(available_channels)
        })
        
    except Exception as e:
        return error_response(f"Failed to fetch channel status: {str(e)}", 500)

