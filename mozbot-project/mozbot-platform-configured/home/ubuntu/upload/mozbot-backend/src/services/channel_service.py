"""
Multi-Channel Communication Service
Handles messaging across different platforms (Telegram, WhatsApp, Messenger, etc.)
"""

import requests
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.models.conversation import Conversation, Message
from src.models.chatbot import Chatbot
from src.services.automation_service import automation_service
import logging

logger = logging.getLogger(__name__)

class ChannelAdapter(ABC):
    """Abstract base class for channel adapters"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.channel_type = self.get_channel_type()
    
    @abstractmethod
    def get_channel_type(self) -> str:
        """Return the channel type identifier"""
        pass
    
    @abstractmethod
    def send_message(self, recipient_id: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send a message to the recipient"""
        pass
    
    @abstractmethod
    def receive_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message from webhook"""
        pass
    
    @abstractmethod
    def validate_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Validate incoming webhook data"""
        pass
    
    @abstractmethod
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from the platform"""
        pass

class TelegramAdapter(ChannelAdapter):
    """Telegram Bot API adapter"""
    
    def get_channel_type(self) -> str:
        return 'telegram'
    
    def send_message(self, recipient_id: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send message via Telegram Bot API"""
        try:
            bot_token = self.config.get('bot_token')
            if not bot_token:
                return {'success': False, 'error': 'Bot token not configured'}
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            payload = {
                'chat_id': recipient_id,
                'text': message,
                'parse_mode': kwargs.get('parse_mode', 'HTML')
            }
            
            # Add inline keyboard if provided
            if 'reply_markup' in kwargs:
                payload['reply_markup'] = kwargs['reply_markup']
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response.json()['result']['message_id'],
                    'platform_response': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Telegram API error: {response.status_code}',
                    'response': response.text
                }
                
        except Exception as e:
            logger.error(f"Telegram send message failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def receive_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming Telegram message"""
        try:
            if 'message' not in webhook_data:
                return {'success': False, 'error': 'No message in webhook data'}
            
            message_data = webhook_data['message']
            
            return {
                'success': True,
                'user_id': str(message_data['from']['id']),
                'user_name': message_data['from'].get('first_name', '') + ' ' + message_data['from'].get('last_name', ''),
                'user_username': message_data['from'].get('username'),
                'message_text': message_data.get('text', ''),
                'message_id': str(message_data['message_id']),
                'chat_id': str(message_data['chat']['id']),
                'timestamp': datetime.fromtimestamp(message_data['date']),
                'platform_data': message_data
            }
            
        except Exception as e:
            logger.error(f"Telegram receive message failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def validate_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Validate Telegram webhook"""
        try:
            # Basic validation - check for required fields
            if 'update_id' not in webhook_data:
                return False
            
            if 'message' in webhook_data:
                message = webhook_data['message']
                required_fields = ['message_id', 'from', 'chat', 'date']
                return all(field in message for field in required_fields)
            
            return True
            
        except Exception as e:
            logger.error(f"Telegram webhook validation failed: {str(e)}")
            return False
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get Telegram user information"""
        try:
            bot_token = self.config.get('bot_token')
            if not bot_token:
                return {'success': False, 'error': 'Bot token not configured'}
            
            url = f"https://api.telegram.org/bot{bot_token}/getChat"
            
            response = requests.get(url, params={'chat_id': user_id}, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()['result']
                return {
                    'success': True,
                    'user_id': str(user_data['id']),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'username': user_data.get('username', ''),
                    'type': user_data.get('type', 'private')
                }
            else:
                return {'success': False, 'error': f'Telegram API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Telegram get user info failed: {str(e)}")
            return {'success': False, 'error': str(e)}

class WhatsAppAdapter(ChannelAdapter):
    """WhatsApp Business API adapter"""
    
    def get_channel_type(self) -> str:
        return 'whatsapp'
    
    def send_message(self, recipient_id: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send message via WhatsApp Business API"""
        try:
            access_token = self.config.get('access_token')
            phone_number_id = self.config.get('phone_number_id')
            
            if not access_token or not phone_number_id:
                return {'success': False, 'error': 'WhatsApp credentials not configured'}
            
            url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': recipient_id,
                'type': 'text',
                'text': {'body': message}
            }
            
            # Add template message if provided
            if 'template' in kwargs:
                payload['type'] = 'template'
                payload['template'] = kwargs['template']
                del payload['text']
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response.json()['messages'][0]['id'],
                    'platform_response': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'WhatsApp API error: {response.status_code}',
                    'response': response.text
                }
                
        except Exception as e:
            logger.error(f"WhatsApp send message failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def receive_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming WhatsApp message"""
        try:
            if 'entry' not in webhook_data:
                return {'success': False, 'error': 'No entry in webhook data'}
            
            entry = webhook_data['entry'][0]
            changes = entry['changes'][0]
            value = changes['value']
            
            if 'messages' not in value:
                return {'success': False, 'error': 'No messages in webhook data'}
            
            message_data = value['messages'][0]
            contact_data = value['contacts'][0]
            
            return {
                'success': True,
                'user_id': message_data['from'],
                'user_name': contact_data['profile']['name'],
                'user_phone': message_data['from'],
                'message_text': message_data.get('text', {}).get('body', ''),
                'message_id': message_data['id'],
                'timestamp': datetime.fromtimestamp(int(message_data['timestamp'])),
                'platform_data': message_data
            }
            
        except Exception as e:
            logger.error(f"WhatsApp receive message failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def validate_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Validate WhatsApp webhook"""
        try:
            # Verify webhook signature if configured
            verify_token = self.config.get('verify_token')
            if verify_token:
                # This would implement webhook verification
                pass
            
            # Basic validation
            if 'entry' not in webhook_data:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"WhatsApp webhook validation failed: {str(e)}")
            return False
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get WhatsApp user information"""
        try:
            # WhatsApp Business API doesn't provide user info endpoint
            # Return basic info based on phone number
            return {
                'success': True,
                'user_id': user_id,
                'phone_number': user_id,
                'platform': 'whatsapp'
            }
            
        except Exception as e:
            logger.error(f"WhatsApp get user info failed: {str(e)}")
            return {'success': False, 'error': str(e)}

class MessengerAdapter(ChannelAdapter):
    """Facebook Messenger adapter"""
    
    def get_channel_type(self) -> str:
        return 'messenger'
    
    def send_message(self, recipient_id: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send message via Messenger API"""
        try:
            access_token = self.config.get('access_token')
            if not access_token:
                return {'success': False, 'error': 'Access token not configured'}
            
            url = f"https://graph.facebook.com/v18.0/me/messages"
            
            params = {'access_token': access_token}
            
            payload = {
                'recipient': {'id': recipient_id},
                'message': {'text': message}
            }
            
            # Add quick replies if provided
            if 'quick_replies' in kwargs:
                payload['message']['quick_replies'] = kwargs['quick_replies']
            
            response = requests.post(url, json=payload, params=params, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response.json()['message_id'],
                    'platform_response': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Messenger API error: {response.status_code}',
                    'response': response.text
                }
                
        except Exception as e:
            logger.error(f"Messenger send message failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def receive_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming Messenger message"""
        try:
            if 'entry' not in webhook_data:
                return {'success': False, 'error': 'No entry in webhook data'}
            
            entry = webhook_data['entry'][0]
            messaging = entry['messaging'][0]
            
            if 'message' not in messaging:
                return {'success': False, 'error': 'No message in webhook data'}
            
            message_data = messaging['message']
            sender = messaging['sender']
            
            return {
                'success': True,
                'user_id': sender['id'],
                'message_text': message_data.get('text', ''),
                'message_id': message_data['mid'],
                'timestamp': datetime.fromtimestamp(messaging['timestamp'] / 1000),
                'platform_data': messaging
            }
            
        except Exception as e:
            logger.error(f"Messenger receive message failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def validate_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Validate Messenger webhook"""
        try:
            # Basic validation
            if 'entry' not in webhook_data:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Messenger webhook validation failed: {str(e)}")
            return False
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get Messenger user information"""
        try:
            access_token = self.config.get('access_token')
            if not access_token:
                return {'success': False, 'error': 'Access token not configured'}
            
            url = f"https://graph.facebook.com/v18.0/{user_id}"
            
            params = {
                'access_token': access_token,
                'fields': 'first_name,last_name,profile_pic'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'user_id': user_id,
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'profile_pic': user_data.get('profile_pic', ''),
                    'platform': 'messenger'
                }
            else:
                return {'success': False, 'error': f'Messenger API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Messenger get user info failed: {str(e)}")
            return {'success': False, 'error': str(e)}

class DiscordAdapter(ChannelAdapter):
    """Discord Bot adapter"""
    
    def get_channel_type(self) -> str:
        return 'discord'
    
    def send_message(self, recipient_id: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send message via Discord API"""
        try:
            bot_token = self.config.get('bot_token')
            if not bot_token:
                return {'success': False, 'error': 'Bot token not configured'}
            
            url = f"https://discord.com/api/v10/channels/{recipient_id}/messages"
            
            headers = {
                'Authorization': f'Bot {bot_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {'content': message}
            
            # Add embeds if provided
            if 'embeds' in kwargs:
                payload['embeds'] = kwargs['embeds']
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response.json()['id'],
                    'platform_response': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Discord API error: {response.status_code}',
                    'response': response.text
                }
                
        except Exception as e:
            logger.error(f"Discord send message failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def receive_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming Discord message"""
        try:
            if 't' not in webhook_data or webhook_data['t'] != 'MESSAGE_CREATE':
                return {'success': False, 'error': 'Not a message event'}
            
            message_data = webhook_data['d']
            
            return {
                'success': True,
                'user_id': message_data['author']['id'],
                'user_name': message_data['author']['username'],
                'message_text': message_data['content'],
                'message_id': message_data['id'],
                'channel_id': message_data['channel_id'],
                'timestamp': datetime.fromisoformat(message_data['timestamp'].replace('Z', '+00:00')),
                'platform_data': message_data
            }
            
        except Exception as e:
            logger.error(f"Discord receive message failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def validate_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Validate Discord webhook"""
        try:
            # Basic validation
            required_fields = ['t', 'd']
            return all(field in webhook_data for field in required_fields)
            
        except Exception as e:
            logger.error(f"Discord webhook validation failed: {str(e)}")
            return False
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get Discord user information"""
        try:
            bot_token = self.config.get('bot_token')
            if not bot_token:
                return {'success': False, 'error': 'Bot token not configured'}
            
            url = f"https://discord.com/api/v10/users/{user_id}"
            
            headers = {'Authorization': f'Bot {bot_token}'}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'user_id': user_id,
                    'username': user_data['username'],
                    'discriminator': user_data['discriminator'],
                    'avatar': user_data.get('avatar'),
                    'platform': 'discord'
                }
            else:
                return {'success': False, 'error': f'Discord API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Discord get user info failed: {str(e)}")
            return {'success': False, 'error': str(e)}

class ChannelService:
    """Main service for managing multi-channel communications"""
    
    def __init__(self):
        self.adapters = {}
        self.register_default_adapters()
    
    def register_default_adapters(self):
        """Register default channel adapters"""
        self.adapter_classes = {
            'telegram': TelegramAdapter,
            'whatsapp': WhatsAppAdapter,
            'messenger': MessengerAdapter,
            'discord': DiscordAdapter
        }
    
    def register_channel(self, tenant_id: int, channel_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new channel for a tenant"""
        try:
            if channel_type not in self.adapter_classes:
                return {'success': False, 'error': f'Unsupported channel type: {channel_type}'}
            
            adapter_class = self.adapter_classes[channel_type]
            adapter = adapter_class(config)
            
            # Test the adapter configuration
            test_result = self.test_channel_config(adapter)
            if not test_result['success']:
                return {'success': False, 'error': f'Channel configuration test failed: {test_result["error"]}'}
            
            # Store adapter for tenant
            key = f"{tenant_id}:{channel_type}"
            self.adapters[key] = adapter
            
            return {
                'success': True,
                'message': f'{channel_type} channel registered successfully',
                'channel_type': channel_type
            }
            
        except Exception as e:
            logger.error(f"Channel registration failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_message(self, tenant_id: int, channel_type: str, recipient_id: str, 
                    message: str, **kwargs) -> Dict[str, Any]:
        """Send message through specified channel"""
        try:
            adapter = self.get_adapter(tenant_id, channel_type)
            if not adapter:
                return {'success': False, 'error': f'Channel {channel_type} not configured for tenant'}
            
            result = adapter.send_message(recipient_id, message, **kwargs)
            
            # Log message for analytics
            if result['success']:
                self.log_outbound_message(tenant_id, channel_type, recipient_id, message, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Send message failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_webhook(self, tenant_id: int, channel_type: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook from channel"""
        try:
            adapter = self.get_adapter(tenant_id, channel_type)
            if not adapter:
                return {'success': False, 'error': f'Channel {channel_type} not configured for tenant'}
            
            # Validate webhook
            if not adapter.validate_webhook(webhook_data):
                return {'success': False, 'error': 'Invalid webhook data'}
            
            # Process message
            message_result = adapter.receive_message(webhook_data)
            if not message_result['success']:
                return message_result
            
            # Create or find conversation
            conversation = self.get_or_create_conversation(
                tenant_id, 
                channel_type, 
                message_result['user_id'],
                message_result
            )
            
            # Save message
            message = Message(
                conversation_id=conversation.id,
                content=message_result['message_text'],
                sender_type='user',
                platform_message_id=message_result['message_id'],
                meta_data={
                    'channel_type': channel_type,
                    'platform_data': message_result.get('platform_data', {})
                }
            )
            message.save()
            
            # Trigger automation
            automation_service.trigger_automation(
                'message_received',
                tenant_id,
                {
                    'conversation': conversation.to_dict(),
                    'message': message.to_dict(),
                    'channel_type': channel_type
                }
            )
            
            # Generate bot response (this would integrate with your AI service)
            bot_response = self.generate_bot_response(conversation, message)
            if bot_response:
                # Send response back through the same channel
                send_result = self.send_message(
                    tenant_id,
                    channel_type,
                    message_result['user_id'],
                    bot_response
                )
                
                if send_result['success']:
                    # Save bot response
                    bot_message = Message(
                        conversation_id=conversation.id,
                        content=bot_response,
                        sender_type='bot',
                        platform_message_id=send_result.get('message_id'),
                        meta_data={
                            'channel_type': channel_type,
                            'platform_response': send_result.get('platform_response', {})
                        }
                    )
                    bot_message.save()
            
            return {
                'success': True,
                'conversation_id': conversation.id,
                'message_id': message.id,
                'bot_response': bot_response
            }
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_adapter(self, tenant_id: int, channel_type: str) -> Optional[ChannelAdapter]:
        """Get channel adapter for tenant"""
        key = f"{tenant_id}:{channel_type}"
        return self.adapters.get(key)
    
    def get_or_create_conversation(self, tenant_id: int, channel_type: str, 
                                 user_id: str, message_data: Dict[str, Any]) -> Conversation:
        """Get existing conversation or create new one"""
        try:
            # Look for existing conversation
            conversation = Conversation.query.filter_by(
                tenant_id=tenant_id,
                user_id=user_id,
                channel_type=channel_type,
                status='active'
            ).first()
            
            if conversation:
                return conversation
            
            # Create new conversation
            conversation = Conversation(
                tenant_id=tenant_id,
                user_id=user_id,
                channel_type=channel_type,
                user_name=message_data.get('user_name', ''),
                user_email=message_data.get('user_email', ''),
                status='active',
                meta_data={
                    'platform_user_data': message_data.get('platform_data', {}),
                    'first_message_time': datetime.utcnow().isoformat()
                }
            )
            conversation.save()
            
            # Trigger new conversation automation
            automation_service.trigger_automation(
                'new_conversation',
                tenant_id,
                {
                    'conversation': conversation.to_dict(),
                    'channel_type': channel_type
                }
            )
            
            return conversation
            
        except Exception as e:
            logger.error(f"Get or create conversation failed: {str(e)}")
            raise
    
    def generate_bot_response(self, conversation: Conversation, message: Message) -> Optional[str]:
        """Generate bot response (placeholder for AI integration)"""
        try:
            # This would integrate with your AI service (OpenAI, etc.)
            # For now, return a simple response
            
            message_text = message.content.lower()
            
            if any(greeting in message_text for greeting in ['hello', 'hi', 'hey']):
                return "Hello! How can I help you today?"
            elif any(word in message_text for word in ['help', 'support']):
                return "I'm here to help! What do you need assistance with?"
            elif any(word in message_text for word in ['price', 'cost', 'pricing']):
                return "I'd be happy to help with pricing information. Let me connect you with our sales team."
            elif any(word in message_text for word in ['bye', 'goodbye', 'thanks']):
                return "Thank you for contacting us! Have a great day!"
            else:
                return "Thank you for your message. How can I assist you further?"
                
        except Exception as e:
            logger.error(f"Bot response generation failed: {str(e)}")
            return None
    
    def test_channel_config(self, adapter: ChannelAdapter) -> Dict[str, Any]:
        """Test channel adapter configuration"""
        try:
            # This would perform basic connectivity tests
            # For now, just check if required config is present
            
            channel_type = adapter.get_channel_type()
            config = adapter.config
            
            if channel_type == 'telegram':
                if 'bot_token' not in config:
                    return {'success': False, 'error': 'Bot token required for Telegram'}
            elif channel_type == 'whatsapp':
                if 'access_token' not in config or 'phone_number_id' not in config:
                    return {'success': False, 'error': 'Access token and phone number ID required for WhatsApp'}
            elif channel_type == 'messenger':
                if 'access_token' not in config:
                    return {'success': False, 'error': 'Access token required for Messenger'}
            elif channel_type == 'discord':
                if 'bot_token' not in config:
                    return {'success': False, 'error': 'Bot token required for Discord'}
            
            return {'success': True, 'message': 'Configuration valid'}
            
        except Exception as e:
            logger.error(f"Channel config test failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def log_outbound_message(self, tenant_id: int, channel_type: str, recipient_id: str, 
                           message: str, result: Dict[str, Any]):
        """Log outbound message for analytics"""
        try:
            log_data = {
                'tenant_id': tenant_id,
                'channel_type': channel_type,
                'recipient_id': recipient_id,
                'message': message,
                'success': result['success'],
                'timestamp': datetime.utcnow().isoformat(),
                'platform_response': result.get('platform_response', {})
            }
            
            logger.info(f"Outbound message: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Message logging failed: {str(e)}")
    
    def get_supported_channels(self) -> List[Dict[str, Any]]:
        """Get list of supported channels"""
        return [
            {
                'type': 'telegram',
                'name': 'Telegram',
                'description': 'Telegram Bot API integration',
                'required_config': ['bot_token'],
                'optional_config': ['webhook_url']
            },
            {
                'type': 'whatsapp',
                'name': 'WhatsApp Business',
                'description': 'WhatsApp Business API integration',
                'required_config': ['access_token', 'phone_number_id'],
                'optional_config': ['verify_token']
            },
            {
                'type': 'messenger',
                'name': 'Facebook Messenger',
                'description': 'Facebook Messenger Platform integration',
                'required_config': ['access_token'],
                'optional_config': ['verify_token']
            },
            {
                'type': 'discord',
                'name': 'Discord',
                'description': 'Discord Bot integration',
                'required_config': ['bot_token'],
                'optional_config': ['guild_id']
            }
        ]

# Global channel service instance
channel_service = ChannelService()

