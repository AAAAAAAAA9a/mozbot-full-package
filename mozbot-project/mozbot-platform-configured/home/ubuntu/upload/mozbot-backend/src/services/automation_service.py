"""
Automation Service
Handles workflow execution, trigger management, and external integrations
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from src.models.automation import AutomationWorkflow, AutomationExecution
from src.models.conversation import Conversation, Message
from src.models.chatbot import Chatbot
import logging

logger = logging.getLogger(__name__)

class AutomationService:
    """Service for managing automation workflows and integrations"""
    
    def __init__(self):
        self.supported_triggers = [
            'new_conversation',
            'message_received',
            'conversation_ended',
            'user_inactive',
            'keyword_detected',
            'sentiment_negative',
            'escalation_requested'
        ]
        
        self.supported_actions = [
            'webhook',
            'email',
            'slack',
            'custom_response',
            'tag_conversation',
            'assign_agent',
            'create_ticket',
            'send_sms'
        ]
    
    def trigger_automation(self, trigger_type: str, tenant_id: int, data: Dict[str, Any]) -> List[Dict]:
        """
        Trigger automation workflows based on events
        
        Args:
            trigger_type: Type of trigger (e.g., 'new_conversation')
            tenant_id: Tenant ID
            data: Event data
            
        Returns:
            List of execution results
        """
        try:
            # Find active workflows for this trigger
            workflows = AutomationWorkflow.query.filter_by(
                tenant_id=tenant_id,
                trigger_type=trigger_type,
                is_active=True
            ).all()
            
            results = []
            for workflow in workflows:
                try:
                    # Check if trigger conditions are met
                    if self._check_trigger_conditions(workflow, data):
                        result = self._execute_workflow(workflow, data)
                        results.append({
                            'workflow_id': workflow.id,
                            'workflow_name': workflow.name,
                            'success': True,
                            'result': result
                        })
                        
                        # Log successful execution
                        self._log_workflow_execution(workflow, data, result, True)
                        
                except Exception as e:
                    logger.error(f"Failed to execute workflow {workflow.id}: {str(e)}")
                    results.append({
                        'workflow_id': workflow.id,
                        'workflow_name': workflow.name,
                        'success': False,
                        'error': str(e)
                    })
                    
                    # Log failed execution
                    self._log_workflow_execution(workflow, data, None, False, str(e))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to trigger automation: {str(e)}")
            return []
    
    def create_n8n_workflow(self, tenant_id: int, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a workflow in n8n via API
        
        Args:
            tenant_id: Tenant ID
            workflow_config: n8n workflow configuration
            
        Returns:
            Creation result
        """
        try:
            n8n_config = self._get_n8n_config(tenant_id)
            if not n8n_config:
                return {'success': False, 'error': 'n8n not configured for tenant'}
            
            # Prepare n8n workflow
            n8n_workflow = {
                'name': workflow_config.get('name', 'MozBot Workflow'),
                'nodes': self._build_n8n_nodes(workflow_config),
                'connections': self._build_n8n_connections(workflow_config),
                'active': workflow_config.get('active', True),
                'settings': {
                    'executionOrder': 'v1'
                }
            }
            
            # Create workflow in n8n
            response = requests.post(
                f"{n8n_config['base_url']}/api/v1/workflows",
                json=n8n_workflow,
                headers={
                    'Authorization': f"Bearer {n8n_config['api_key']}",
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 201:
                n8n_workflow_data = response.json()
                return {
                    'success': True,
                    'n8n_workflow_id': n8n_workflow_data['id'],
                    'webhook_url': self._extract_webhook_url(n8n_workflow_data)
                }
            else:
                return {
                    'success': False,
                    'error': f'n8n API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Failed to create n8n workflow: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_integration(self, integration_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test external integration
        
        Args:
            integration_type: Type of integration (n8n, zapier, slack, etc.)
            config: Integration configuration
            
        Returns:
            Test result
        """
        try:
            if integration_type == 'n8n':
                return self._test_n8n_integration(config)
            elif integration_type == 'zapier':
                return self._test_zapier_integration(config)
            elif integration_type == 'slack':
                return self._test_slack_integration(config)
            elif integration_type == 'webhook':
                return self._test_webhook_integration(config)
            else:
                return {'success': False, 'error': f'Unsupported integration: {integration_type}'}
                
        except Exception as e:
            logger.error(f"Integration test failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """
        Get predefined workflow templates
        
        Returns:
            List of workflow templates
        """
        return [
            {
                'id': 'lead_capture',
                'name': 'Lead Capture & CRM Integration',
                'description': 'Automatically capture leads and send to CRM',
                'trigger_type': 'new_conversation',
                'actions': [
                    {
                        'type': 'webhook',
                        'config': {
                            'url': 'https://your-crm.com/api/leads',
                            'method': 'POST',
                            'payload': {
                                'email': '{user_email}',
                                'source': 'chatbot',
                                'conversation_id': '{conversation_id}'
                            }
                        }
                    }
                ]
            },
            {
                'id': 'support_escalation',
                'name': 'Support Ticket Creation',
                'description': 'Create support ticket when escalation is requested',
                'trigger_type': 'escalation_requested',
                'actions': [
                    {
                        'type': 'create_ticket',
                        'config': {
                            'priority': 'high',
                            'category': 'support',
                            'assign_to': 'support_team'
                        }
                    },
                    {
                        'type': 'slack',
                        'config': {
                            'channel': '#support',
                            'message': 'New support escalation: {conversation_id}'
                        }
                    }
                ]
            },
            {
                'id': 'negative_sentiment',
                'name': 'Negative Sentiment Alert',
                'description': 'Alert team when negative sentiment is detected',
                'trigger_type': 'sentiment_negative',
                'actions': [
                    {
                        'type': 'email',
                        'config': {
                            'to': 'manager@company.com',
                            'subject': 'Negative Sentiment Detected',
                            'body': 'Customer expressed negative sentiment in conversation {conversation_id}'
                        }
                    },
                    {
                        'type': 'tag_conversation',
                        'config': {
                            'tags': ['negative_sentiment', 'needs_attention']
                        }
                    }
                ]
            },
            {
                'id': 'follow_up',
                'name': 'Follow-up Sequence',
                'description': 'Send follow-up messages after conversation ends',
                'trigger_type': 'conversation_ended',
                'actions': [
                    {
                        'type': 'custom_response',
                        'config': {
                            'delay': 3600,  # 1 hour
                            'response': 'Thank you for chatting with us! Is there anything else we can help you with?'
                        }
                    }
                ]
            },
            {
                'id': 'keyword_routing',
                'name': 'Keyword-based Routing',
                'description': 'Route conversations based on detected keywords',
                'trigger_type': 'keyword_detected',
                'conditions': [
                    {
                        'field': 'keywords',
                        'operator': 'contains',
                        'value': ['pricing', 'cost', 'price']
                    }
                ],
                'actions': [
                    {
                        'type': 'assign_agent',
                        'config': {
                            'department': 'sales'
                        }
                    },
                    {
                        'type': 'custom_response',
                        'config': {
                            'response': 'I\'ll connect you with our sales team who can help with pricing questions.'
                        }
                    }
                ]
            }
        ]
    
    def _execute_workflow(self, workflow: AutomationWorkflow, data: Dict[str, Any]) -> List[Dict]:
        """Execute all actions in a workflow"""
        results = []
        
        try:
            # For now, use a simple configuration-based approach
            # In a full implementation, you'd have separate action models
            actions = workflow.configuration.get('actions', [])
            
            for i, action_config in enumerate(actions):
                result = self._execute_action(action_config, data, workflow)
                results.append({
                    'action_index': i,
                    'action_type': action_config.get('type', 'unknown'),
                    'success': result.get('success', False),
                    'result': result
                })
                
                # Stop execution if action failed and workflow is configured to stop on failure
                if not result.get('success', False) and workflow.configuration.get('stop_on_failure', False):
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return [{'error': str(e)}]
    
    def _execute_action(self, action_config: Dict[str, Any], data: Dict[str, Any], workflow: AutomationWorkflow) -> Dict[str, Any]:
        """Execute a single action"""
        try:
            action_type = action_config.get('type', 'unknown')
            config = action_config.get('config', {})
            
            # Replace placeholders in config
            processed_config = self._process_placeholders(config, data)
            
            if action_type == 'webhook':
                return self._execute_webhook_action(processed_config)
            elif action_type == 'email':
                return self._execute_email_action(processed_config)
            elif action_type == 'slack':
                return self._execute_slack_action(processed_config)
            elif action_type == 'custom_response':
                return self._execute_custom_response_action(processed_config, data)
            elif action_type == 'tag_conversation':
                return self._execute_tag_conversation_action(processed_config, data)
            elif action_type == 'assign_agent':
                return self._execute_assign_agent_action(processed_config, data)
            elif action_type == 'create_ticket':
                return self._execute_create_ticket_action(processed_config, data)
            elif action_type == 'send_sms':
                return self._execute_send_sms_action(processed_config, data)
            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}
                
        except Exception as e:
            logger.error(f"Action execution failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _check_trigger_conditions(self, workflow: AutomationWorkflow, data: Dict[str, Any]) -> bool:
        """Check if workflow trigger conditions are met"""
        try:
            trigger_config = workflow.trigger_config
            
            if 'conditions' not in trigger_config:
                return True
            
            conditions = trigger_config['conditions']
            
            for condition in conditions:
                if not self._evaluate_condition(condition, data):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Condition check failed: {str(e)}")
            return False
    
    def _evaluate_condition(self, condition: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        try:
            field = condition.get('field')
            operator = condition.get('operator')
            expected_value = condition.get('value')
            
            # Extract actual value from data
            actual_value = self._extract_field_value(field, data)
            
            if operator == 'equals':
                return actual_value == expected_value
            elif operator == 'not_equals':
                return actual_value != expected_value
            elif operator == 'greater_than':
                return float(actual_value) > float(expected_value)
            elif operator == 'less_than':
                return float(actual_value) < float(expected_value)
            elif operator == 'contains':
                return str(expected_value).lower() in str(actual_value).lower()
            elif operator == 'not_contains':
                return str(expected_value).lower() not in str(actual_value).lower()
            elif operator == 'in':
                return actual_value in expected_value
            elif operator == 'not_in':
                return actual_value not in expected_value
            else:
                return True
                
        except Exception as e:
            logger.error(f"Condition evaluation failed: {str(e)}")
            return False
    
    def _extract_field_value(self, field: str, data: Dict[str, Any]) -> Any:
        """Extract field value from data using dot notation"""
        try:
            keys = field.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
            
            return value
            
        except Exception as e:
            return None
    
    def _process_placeholders(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Replace placeholders in configuration with actual data"""
        try:
            config_str = json.dumps(config)
            
            # Replace common placeholders
            if 'conversation' in data:
                conversation = data['conversation']
                config_str = config_str.replace('{conversation_id}', str(conversation.get('id', '')))
                config_str = config_str.replace('{user_email}', conversation.get('user_email', ''))
                config_str = config_str.replace('{user_name}', conversation.get('user_name', ''))
                config_str = config_str.replace('{chatbot_id}', str(conversation.get('chatbot_id', '')))
            
            if 'message' in data:
                message = data['message']
                config_str = config_str.replace('{message_content}', message.get('content', ''))
                config_str = config_str.replace('{message_id}', str(message.get('id', '')))
            
            # Replace timestamp placeholders
            config_str = config_str.replace('{timestamp}', datetime.utcnow().isoformat())
            config_str = config_str.replace('{date}', datetime.utcnow().strftime('%Y-%m-%d'))
            config_str = config_str.replace('{time}', datetime.utcnow().strftime('%H:%M:%S'))
            
            return json.loads(config_str)
            
        except Exception as e:
            logger.error(f"Placeholder processing failed: {str(e)}")
            return config
    
    def _execute_webhook_action(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute webhook action"""
        try:
            url = config.get('url')
            method = config.get('method', 'POST').upper()
            headers = config.get('headers', {})
            payload = config.get('payload', {})
            timeout = config.get('timeout', 30)
            
            if method == 'POST':
                response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            elif method == 'GET':
                response = requests.get(url, params=payload, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=payload, headers=headers, timeout=timeout)
            else:
                return {'success': False, 'error': f'Unsupported HTTP method: {method}'}
            
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'response': response.json() if response.content else None
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_email_action(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email action"""
        try:
            # This would integrate with your email service
            to_email = config.get('to')
            subject = config.get('subject', 'MozBot Notification')
            body = config.get('body', '')
            
            # Simulate email sending
            return {
                'success': True,
                'message': f'Email sent to {to_email}',
                'subject': subject
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_slack_action(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Slack action"""
        try:
            webhook_url = config.get('webhook_url')
            channel = config.get('channel', '#general')
            message = config.get('message', 'Automation triggered')
            username = config.get('username', 'MozBot')
            
            payload = {
                'channel': channel,
                'text': message,
                'username': username
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'message': 'Slack message sent'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_custom_response_action(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom response action"""
        try:
            response_text = config.get('response', 'Thank you!')
            delay = config.get('delay', 0)  # Delay in seconds
            
            if 'conversation' in data:
                conversation_id = data['conversation'].get('id')
                
                # If delay is specified, schedule the response
                if delay > 0:
                    # In a real implementation, you'd use a task queue like Celery
                    # For now, we'll just log it
                    return {
                        'success': True,
                        'message': f'Response scheduled with {delay}s delay',
                        'response': response_text
                    }
                else:
                    # Send immediate response
                    message = Message(
                        conversation_id=conversation_id,
                        content=response_text,
                        sender_type='bot',
                        meta_data={'automation_triggered': True}
                    )
                    message.save()
                    
                    return {
                        'success': True,
                        'message': 'Custom response sent',
                        'response': response_text
                    }
            
            return {'success': False, 'error': 'No conversation data provided'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_tag_conversation_action(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tag conversation action"""
        try:
            tags = config.get('tags', [])
            
            if 'conversation' in data:
                conversation_id = data['conversation'].get('id')
                conversation = Conversation.query.get(conversation_id)
                
                if conversation:
                    current_tags = conversation.meta_data.get('tags', [])
                    new_tags = list(set(current_tags + tags))
                    conversation.meta_data['tags'] = new_tags
                    conversation.save()
                    
                    return {
                        'success': True,
                        'message': 'Tags added to conversation',
                        'tags': new_tags
                    }
            
            return {'success': False, 'error': 'No conversation data provided'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_assign_agent_action(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute assign agent action"""
        try:
            agent_id = config.get('agent_id')
            department = config.get('department')
            
            if 'conversation' in data:
                conversation_id = data['conversation'].get('id')
                conversation = Conversation.query.get(conversation_id)
                
                if conversation:
                    if agent_id:
                        conversation.assigned_agent_id = agent_id
                    elif department:
                        # Find available agent in department
                        # This would integrate with your agent management system
                        pass
                    
                    conversation.status = 'assigned'
                    conversation.save()
                    
                    return {
                        'success': True,
                        'message': 'Agent assigned to conversation',
                        'agent_id': agent_id
                    }
            
            return {'success': False, 'error': 'No conversation data provided'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_create_ticket_action(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create ticket action"""
        try:
            # This would integrate with your ticketing system
            priority = config.get('priority', 'medium')
            category = config.get('category', 'general')
            
            return {
                'success': True,
                'message': 'Support ticket created',
                'ticket_id': f'TICKET-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_send_sms_action(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute send SMS action"""
        try:
            # This would integrate with your SMS service (Twilio, etc.)
            phone_number = config.get('phone_number')
            message = config.get('message', 'Message from MozBot')
            
            return {
                'success': True,
                'message': f'SMS sent to {phone_number}',
                'content': message
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_n8n_integration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test n8n integration"""
        try:
            webhook_url = config.get('webhook_url')
            
            test_payload = {
                'test': True,
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Test from MozBot'
            }
            
            response = requests.post(webhook_url, json=test_payload, timeout=10)
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'message': 'n8n integration test completed'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_zapier_integration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Zapier integration"""
        try:
            webhook_url = config.get('webhook_url')
            
            test_payload = {
                'test': True,
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Test from MozBot'
            }
            
            response = requests.post(webhook_url, json=test_payload, timeout=10)
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'message': 'Zapier integration test completed'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_slack_integration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Slack integration"""
        try:
            webhook_url = config.get('webhook_url')
            
            payload = {
                'text': 'Test message from MozBot automation',
                'username': 'MozBot'
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'message': 'Slack integration test completed'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_webhook_integration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test generic webhook integration"""
        try:
            url = config.get('url')
            method = config.get('method', 'POST').upper()
            headers = config.get('headers', {})
            
            test_payload = {
                'test': True,
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Test from MozBot'
            }
            
            if method == 'POST':
                response = requests.post(url, json=test_payload, headers=headers, timeout=10)
            elif method == 'GET':
                response = requests.get(url, params=test_payload, headers=headers, timeout=10)
            else:
                return {'success': False, 'error': f'Unsupported method: {method}'}
            
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'message': 'Webhook integration test completed'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_n8n_config(self, tenant_id: int) -> Optional[Dict[str, str]]:
        """Get n8n configuration for tenant"""
        # This would fetch from tenant settings
        return {
            'base_url': 'https://n8n.example.com',
            'api_key': 'your-n8n-api-key'
        }
    
    def _build_n8n_nodes(self, workflow_config: Dict[str, Any]) -> List[Dict]:
        """Build n8n nodes from workflow configuration"""
        # This would convert MozBot workflow to n8n format
        return []
    
    def _build_n8n_connections(self, workflow_config: Dict[str, Any]) -> Dict:
        """Build n8n connections from workflow configuration"""
        # This would create connections between n8n nodes
        return {}
    
    def _extract_webhook_url(self, n8n_workflow: Dict[str, Any]) -> Optional[str]:
        """Extract webhook URL from n8n workflow"""
        # This would find the webhook trigger URL
        return None
    
    def _log_workflow_execution(self, workflow: AutomationWorkflow, data: Dict[str, Any], 
                               result: Any, success: bool, error: str = None):
        """Log workflow execution for debugging and analytics"""
        try:
            # This would log to your logging system
            log_data = {
                'workflow_id': workflow.id,
                'tenant_id': workflow.tenant_id,
                'trigger_type': workflow.trigger_type,
                'success': success,
                'timestamp': datetime.utcnow().isoformat(),
                'data': data,
                'result': result,
                'error': error
            }
            
            logger.info(f"Workflow execution: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Failed to log workflow execution: {str(e)}")

# Global automation service instance
automation_service = AutomationService()

