from src.models import db, BaseModel
from datetime import datetime

class AutomationWorkflow(BaseModel):
    __tablename__ = 'automation_workflows'
    
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    chatbot_id = db.Column(db.String(36), db.ForeignKey('chatbots.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    trigger_events = db.Column(db.JSON, nullable=False)  # Array of event types
    webhook_url = db.Column(db.String(500))  # n8n webhook URL
    is_active = db.Column(db.Boolean, default=True)
    configuration = db.Column(db.JSON, default={})
    
    # Relationships
    chatbot = db.relationship('Chatbot', back_populates='automation_workflows')
    executions = db.relationship('AutomationExecution', back_populates='workflow', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AutomationWorkflow {self.name}>'
    
    def to_dict(self, include_stats=False):
        data = super().to_dict()
        
        if include_stats:
            data['stats'] = {
                'total_executions': len(self.executions) if self.executions else 0,
                'successful_executions': len([e for e in self.executions if e.status == 'success']) if self.executions else 0,
                'failed_executions': len([e for e in self.executions if e.status == 'failed']) if self.executions else 0
            }
        
        return data
    
    def should_trigger(self, event_type):
        """Check if workflow should trigger for given event type"""
        return event_type in self.trigger_events and self.is_active
    
    def execute(self, event_type, payload):
        """Execute the workflow and log the execution"""
        execution = AutomationExecution(
            tenant_id=self.tenant_id,
            workflow_id=self.id,
            trigger_event=event_type,
            payload=payload,
            status='pending'
        )
        execution.save()
        
        # TODO: Implement actual webhook call to n8n
        # For now, just mark as success
        execution.status = 'success'
        execution.response = {'message': 'Workflow executed successfully'}
        execution.save()
        
        return execution

class AutomationExecution(BaseModel):
    __tablename__ = 'automation_executions'
    
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    workflow_id = db.Column(db.String(36), db.ForeignKey('automation_workflows.id'), nullable=False)
    trigger_event = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.JSON)
    status = db.Column(db.String(50), nullable=False)  # 'success', 'failed', 'pending'
    response = db.Column(db.JSON)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = db.relationship('AutomationWorkflow', back_populates='executions')
    
    def __repr__(self):
        return f'<AutomationExecution {self.id}>'

