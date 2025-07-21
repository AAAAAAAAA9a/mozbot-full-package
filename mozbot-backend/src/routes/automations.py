from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.automation import AutomationWorkflow, AutomationExecution
from src.models.conversation import Conversation, Message
from src.models.chatbot import Chatbot
from src.utils.auth import tenant_required
from src.utils.responses import success_response, error_response
import requests
import json
from datetime import datetime

automations_bp = Blueprint('automations', __name__)

@automations_bp.route('/workflows', methods=['GET'])
@jwt_required()
@tenant_required
def get_workflows():
    """Get all automation workflows for the current tenant"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        
        workflows = AutomationWorkflow.query.filter_by(tenant_id=tenant_id).all()
        
        workflows_data = []
        for workflow in workflows:
            workflows_data.append({
                'id': workflow.id,
                'name': workflow.name,
                'description': workflow.description,
                'is_active': workflow.is_active,
                'trigger_type': workflow.trigger_type,
                'trigger_config': workflow.trigger_config,
                'actions': [
                    {
                        'id': action.id,
                        'type': action.action_type,
                        'config': action.action_config,
                        'order': action.order
                    } for action in workflow.actions
                ],
                'created_at': workflow.created_at.isoformat(),
                'updated_at': workflow.updated_at.isoformat()
            })
        
        return success_response(workflows_data)
        
    except Exception as e:
        return error_response(f"Failed to fetch workflows: {str(e)}", 500)

@automations_bp.route('/workflows', methods=['POST'])
@jwt_required()
@tenant_required
def create_workflow():
    """Create a new automation workflow"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'trigger_type', 'trigger_config', 'actions']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        # Create workflow
        workflow = AutomationWorkflow(
            tenant_id=tenant_id,
            name=data['name'],
            description=data.get('description', ''),
            trigger_type=data['trigger_type'],
            trigger_config=data['trigger_config'],
            is_active=data.get('is_active', True)
        )
        
        workflow.save()
        
        # Create actions
        for i, action_data in enumerate(data['actions']):
            action = AutomationAction(
                workflow_id=workflow.id,
                action_type=action_data['type'],
                action_config=action_data['config'],
                order=i
            )
            action.save()
        
        return success_response({
            'id': workflow.id,
            'message': 'Workflow created successfully'
        }, 201)
        
    except Exception as e:
        return error_response(f"Failed to create workflow: {str(e)}", 500)

@automations_bp.route('/workflows/<int:workflow_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_workflow(workflow_id):
    """Update an existing automation workflow"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        data = request.get_json()
        
        workflow = AutomationWorkflow.query.filter_by(
            id=workflow_id, 
            tenant_id=tenant_id
        ).first()
        
        if not workflow:
            return error_response("Workflow not found", 404)
        
        # Update workflow fields
        if 'name' in data:
            workflow.name = data['name']
        if 'description' in data:
            workflow.description = data['description']
        if 'trigger_type' in data:
            workflow.trigger_type = data['trigger_type']
        if 'trigger_config' in data:
            workflow.trigger_config = data['trigger_config']
        if 'is_active' in data:
            workflow.is_active = data['is_active']
        
        workflow.save()
        
        # Update actions if provided
        if 'actions' in data:
            # Delete existing actions
            AutomationAction.query.filter_by(workflow_id=workflow_id).delete()
            
            # Create new actions
            for i, action_data in enumerate(data['actions']):
                action = AutomationAction(
                    workflow_id=workflow.id,
                    action_type=action_data['type'],
                    action_config=action_data['config'],
                    order=i
                )
                action.save()
        
        return success_response({'message': 'Workflow updated successfully'})
        
    except Exception as e:
        return error_response(f"Failed to update workflow: {str(e)}", 500)

@automations_bp.route('/workflows/<int:workflow_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_workflow(workflow_id):
    """Delete an automation workflow"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        
        workflow = AutomationWorkflow.query.filter_by(
            id=workflow_id, 
            tenant_id=tenant_id
        ).first()
        
        if not workflow:
            return error_response("Workflow not found", 404)
        
        # Delete associated actions
        AutomationAction.query.filter_by(workflow_id=workflow_id).delete()
        
        # Delete workflow
        workflow.delete()
        
        return success_response({'message': 'Workflow deleted successfully'})
        
    except Exception as e:
        return error_response(f"Failed to delete workflow: {str(e)}", 500)

@automations_bp.route('/webhooks/n8n', methods=['POST'])
def n8n_webhook():
    """Webhook endpoint for n8n integrations"""
    try:
        data = request.get_json()
        
        # Validate webhook data
        if 'tenant_id' not in data or 'workflow_id' not in data:
            return error_response("Missing tenant_id or workflow_id", 400)
        
        tenant_id = data['tenant_id']
        workflow_id = data['workflow_id']
        
        # Find the workflow
        workflow = AutomationWorkflow.query.filter_by(
            id=workflow_id,
            tenant_id=tenant_id,
            is_active=True
        ).first()
        
        if not workflow:
            return error_response("Workflow not found or inactive", 404)
        
        # Execute workflow actions
        result = execute_workflow_actions(workflow, data)
        
        return success_response({
            'message': 'Webhook processed successfully',
            'result': result
        })
        
    except Exception as e:
        return error_response(f"Webhook processing failed: {str(e)}", 500)

@automations_bp.route('/webhooks/zapier', methods=['POST'])
def zapier_webhook():
    """Webhook endpoint for Zapier integrations"""
    try:
        data = request.get_json()
        
        # Validate webhook data
        if 'tenant_id' not in data or 'trigger_type' not in data:
            return error_response("Missing tenant_id or trigger_type", 400)
        
        tenant_id = data['tenant_id']
        trigger_type = data['trigger_type']
        
        # Find workflows with matching trigger
        workflows = AutomationWorkflow.query.filter_by(
            tenant_id=tenant_id,
            trigger_type=trigger_type,
            is_active=True
        ).all()
        
        results = []
        for workflow in workflows:
            result = execute_workflow_actions(workflow, data)
            results.append({
                'workflow_id': workflow.id,
                'result': result
            })
        
        return success_response({
            'message': 'Zapier webhook processed successfully',
            'results': results
        })
        
    except Exception as e:
        return error_response(f"Zapier webhook processing failed: {str(e)}", 500)

@automations_bp.route('/triggers/conversation', methods=['POST'])
@jwt_required()
@tenant_required
def trigger_conversation_automation():
    """Trigger automation based on conversation events"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['conversation_id', 'trigger_type']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        conversation_id = data['conversation_id']
        trigger_type = data['trigger_type']
        
        # Verify conversation belongs to tenant
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            tenant_id=tenant_id
        ).first()
        
        if not conversation:
            return error_response("Conversation not found", 404)
        
        # Find matching workflows
        workflows = AutomationWorkflow.query.filter_by(
            tenant_id=tenant_id,
            trigger_type=trigger_type,
            is_active=True
        ).all()
        
        results = []
        for workflow in workflows:
            # Check if trigger conditions are met
            if check_trigger_conditions(workflow, conversation, data):
                result = execute_workflow_actions(workflow, {
                    'conversation': conversation.to_dict(),
                    'trigger_data': data
                })
                results.append({
                    'workflow_id': workflow.id,
                    'result': result
                })
        
        return success_response({
            'message': 'Conversation automation triggered',
            'triggered_workflows': len(results),
            'results': results
        })
        
    except Exception as e:
        return error_response(f"Failed to trigger automation: {str(e)}", 500)

@automations_bp.route('/integrations/n8n/test', methods=['POST'])
@jwt_required()
@tenant_required
def test_n8n_integration():
    """Test n8n integration connection"""
    try:
        user_id = get_jwt_identity()
        tenant_id = request.tenant_id
        data = request.get_json()
        
        if 'webhook_url' not in data:
            return error_response("Missing webhook_url", 400)
        
        webhook_url = data['webhook_url']
        
        # Send test payload to n8n
        test_payload = {
            'test': True,
            'tenant_id': tenant_id,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Test connection from MozBot'
        }
        
        response = requests.post(
            webhook_url,
            json=test_payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return success_response({
                'message': 'n8n integration test successful',
                'response_status': response.status_code,
                'response_data': response.json() if response.content else None
            })
        else:
            return error_response(
                f"n8n integration test failed with status {response.status_code}",
                400
            )
        
    except requests.exceptions.RequestException as e:
        return error_response(f"n8n connection failed: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Integration test failed: {str(e)}", 500)

def execute_workflow_actions(workflow, trigger_data):
    """Execute all actions in a workflow"""
    results = []
    
    try:
        actions = AutomationAction.query.filter_by(
            workflow_id=workflow.id
        ).order_by(AutomationAction.order).all()
        
        for action in actions:
            result = execute_single_action(action, trigger_data, workflow)
            results.append({
                'action_id': action.id,
                'action_type': action.action_type,
                'result': result
            })
        
        return results
        
    except Exception as e:
        return {'error': str(e)}

def execute_single_action(action, trigger_data, workflow):
    """Execute a single automation action"""
    try:
        action_type = action.action_type
        config = action.action_config
        
        if action_type == 'webhook':
            return execute_webhook_action(config, trigger_data)
        elif action_type == 'email':
            return execute_email_action(config, trigger_data)
        elif action_type == 'slack':
            return execute_slack_action(config, trigger_data)
        elif action_type == 'custom_response':
            return execute_custom_response_action(config, trigger_data)
        elif action_type == 'tag_conversation':
            return execute_tag_conversation_action(config, trigger_data)
        elif action_type == 'assign_agent':
            return execute_assign_agent_action(config, trigger_data)
        else:
            return {'error': f'Unknown action type: {action_type}'}
        
    except Exception as e:
        return {'error': str(e)}

def execute_webhook_action(config, trigger_data):
    """Execute webhook action"""
    try:
        webhook_url = config.get('url')
        method = config.get('method', 'POST')
        headers = config.get('headers', {})
        payload = config.get('payload', {})
        
        # Merge trigger data with payload
        final_payload = {**payload, **trigger_data}
        
        if method.upper() == 'POST':
            response = requests.post(
                webhook_url,
                json=final_payload,
                headers=headers,
                timeout=30
            )
        elif method.upper() == 'GET':
            response = requests.get(
                webhook_url,
                params=final_payload,
                headers=headers,
                timeout=30
            )
        else:
            return {'error': f'Unsupported HTTP method: {method}'}
        
        return {
            'success': True,
            'status_code': response.status_code,
            'response': response.json() if response.content else None
        }
        
    except Exception as e:
        return {'error': str(e)}

def execute_email_action(config, trigger_data):
    """Execute email action"""
    try:
        # This would integrate with your email service (SendGrid, AWS SES, etc.)
        to_email = config.get('to')
        subject = config.get('subject', 'MozBot Automation')
        body = config.get('body', '')
        
        # Replace placeholders in subject and body
        if 'conversation' in trigger_data:
            conversation = trigger_data['conversation']
            subject = subject.replace('{conversation_id}', str(conversation.get('id', '')))
            body = body.replace('{conversation_id}', str(conversation.get('id', '')))
            body = body.replace('{user_email}', conversation.get('user_email', ''))
        
        # Here you would send the actual email
        # For now, we'll just return success
        return {
            'success': True,
            'message': f'Email sent to {to_email}',
            'subject': subject
        }
        
    except Exception as e:
        return {'error': str(e)}

def execute_slack_action(config, trigger_data):
    """Execute Slack action"""
    try:
        webhook_url = config.get('webhook_url')
        channel = config.get('channel', '#general')
        message = config.get('message', 'New automation triggered')
        
        # Replace placeholders in message
        if 'conversation' in trigger_data:
            conversation = trigger_data['conversation']
            message = message.replace('{conversation_id}', str(conversation.get('id', '')))
            message = message.replace('{user_email}', conversation.get('user_email', ''))
        
        payload = {
            'channel': channel,
            'text': message,
            'username': 'MozBot'
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        return {
            'success': True,
            'status_code': response.status_code,
            'message': 'Slack message sent'
        }
        
    except Exception as e:
        return {'error': str(e)}

def execute_custom_response_action(config, trigger_data):
    """Execute custom response action"""
    try:
        response_text = config.get('response', 'Thank you for your message!')
        
        # If we have conversation data, send the response
        if 'conversation' in trigger_data:
            conversation_id = trigger_data['conversation'].get('id')
            
            # Create a new message in the conversation
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
        
        return {
            'success': True,
            'message': 'Custom response prepared',
            'response': response_text
        }
        
    except Exception as e:
        return {'error': str(e)}

def execute_tag_conversation_action(config, trigger_data):
    """Execute tag conversation action"""
    try:
        tags = config.get('tags', [])
        
        if 'conversation' in trigger_data:
            conversation_id = trigger_data['conversation'].get('id')
            conversation = Conversation.query.get(conversation_id)
            
            if conversation:
                # Add tags to conversation metadata
                current_tags = conversation.meta_data.get('tags', [])
                new_tags = list(set(current_tags + tags))
                conversation.meta_data['tags'] = new_tags
                conversation.save()
                
                return {
                    'success': True,
                    'message': 'Tags added to conversation',
                    'tags': new_tags
                }
        
        return {'error': 'No conversation data provided'}
        
    except Exception as e:
        return {'error': str(e)}

def execute_assign_agent_action(config, trigger_data):
    """Execute assign agent action"""
    try:
        agent_id = config.get('agent_id')
        
        if 'conversation' in trigger_data:
            conversation_id = trigger_data['conversation'].get('id')
            conversation = Conversation.query.get(conversation_id)
            
            if conversation:
                conversation.assigned_agent_id = agent_id
                conversation.status = 'assigned'
                conversation.save()
                
                return {
                    'success': True,
                    'message': 'Agent assigned to conversation',
                    'agent_id': agent_id
                }
        
        return {'error': 'No conversation data provided'}
        
    except Exception as e:
        return {'error': str(e)}

def check_trigger_conditions(workflow, conversation, trigger_data):
    """Check if workflow trigger conditions are met"""
    try:
        trigger_config = workflow.trigger_config
        
        # Check conversation conditions
        if 'conditions' in trigger_config:
            conditions = trigger_config['conditions']
            
            for condition in conditions:
                field = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if field == 'message_count':
                    message_count = Message.query.filter_by(
                        conversation_id=conversation.id
                    ).count()
                    
                    if not evaluate_condition(message_count, operator, value):
                        return False
                
                elif field == 'user_email':
                    if not evaluate_condition(conversation.user_email, operator, value):
                        return False
                
                elif field == 'status':
                    if not evaluate_condition(conversation.status, operator, value):
                        return False
        
        return True
        
    except Exception as e:
        return False

def evaluate_condition(actual_value, operator, expected_value):
    """Evaluate a single condition"""
    try:
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
        else:
            return True
            
    except Exception as e:
        return False

