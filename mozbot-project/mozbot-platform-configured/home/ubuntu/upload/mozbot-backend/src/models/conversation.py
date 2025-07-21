from src.models import db, BaseModel
from datetime import datetime

class Conversation(BaseModel):
    __tablename__ = 'conversations'
    
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    chatbot_id = db.Column(db.String(36), db.ForeignKey('chatbots.id'), nullable=False)
    channel_type = db.Column(db.String(50), nullable=False)
    channel_user_id = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='active')  # 'active', 'resolved', 'escalated'
    meta_data = db.Column(db.JSON, default={})
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    
    # Relationships
    chatbot = db.relationship('Chatbot', back_populates='conversations')
    messages = db.relationship('Message', back_populates='conversation', cascade='all, delete-orphan', order_by='Message.created_at')
    
    def __repr__(self):
        return f'<Conversation {self.id}>'
    
    def to_dict(self, include_messages=False):
        data = super().to_dict()
        
        if include_messages:
            data['messages'] = [message.to_dict() for message in self.messages]
        else:
            # Include last message for conversation list
            if self.messages:
                last_message = self.messages[-1]
                data['last_message'] = {
                    'content': last_message.content,
                    'sender_type': last_message.sender_type,
                    'created_at': last_message.created_at.isoformat() + 'Z'
                }
        
        return data
    
    def add_message(self, sender_type, content, sender_id=None, message_type='text', meta_data=None):
        """Add a new message to the conversation"""
        message = Message(
            tenant_id=self.tenant_id,
            conversation_id=self.id,
            sender_type=sender_type,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            meta_data=meta_data or {}
        )
        return message.save()
    
    def mark_resolved(self):
        """Mark conversation as resolved"""
        self.status = 'resolved'
        self.ended_at = datetime.utcnow()
        return self.save()
    
    def escalate(self):
        """Escalate conversation to human agent"""
        self.status = 'escalated'
        return self.save()

class Message(BaseModel):
    __tablename__ = 'messages'
    
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # 'user', 'bot', 'agent'
    sender_id = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), default='text')  # 'text', 'image', 'file', 'quick_reply'
    meta_data = db.Column(db.JSON, default={})
    
    # Relationships
    conversation = db.relationship('Conversation', back_populates='messages')
    
    def __repr__(self):
        return f'<Message {self.id}>'

