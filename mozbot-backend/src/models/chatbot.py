from src.models import db, BaseModel

class Chatbot(BaseModel):
    __tablename__ = 'chatbots'
    
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    widget_settings = db.Column(db.JSON, default={})
    ai_settings = db.Column(db.JSON, default={})
    branding = db.Column(db.JSON, default={})
    
    # Relationships
    tenant = db.relationship('Tenant', back_populates='chatbots')
    channels = db.relationship('ChatbotChannel', back_populates='chatbot', cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', back_populates='chatbot', cascade='all, delete-orphan')
    knowledge_articles = db.relationship('KnowledgeArticle', back_populates='chatbot', cascade='all, delete-orphan')
    faqs = db.relationship('FAQ', back_populates='chatbot', cascade='all, delete-orphan')
    automation_workflows = db.relationship('AutomationWorkflow', back_populates='chatbot', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Chatbot {self.name}>'
    
    def to_dict(self, include_stats=False):
        data = super().to_dict()
        
        if include_stats:
            data['stats'] = {
                'total_conversations': len(self.conversations) if self.conversations else 0,
                'active_channels': len([c for c in self.channels if c.is_active]) if self.channels else 0,
                'knowledge_articles': len(self.knowledge_articles) if self.knowledge_articles else 0,
                'faqs': len(self.faqs) if self.faqs else 0
            }
        
        return data

class ChatbotChannel(BaseModel):
    __tablename__ = 'chatbot_channels'
    
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    chatbot_id = db.Column(db.String(36), db.ForeignKey('chatbots.id'), nullable=False)
    channel_type = db.Column(db.String(50), nullable=False)  # 'web', 'telegram', 'whatsapp', 'messenger'
    channel_config = db.Column(db.JSON, default={})
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    chatbot = db.relationship('Chatbot', back_populates='channels')
    
    def __repr__(self):
        return f'<ChatbotChannel {self.channel_type}>'

class KnowledgeArticle(BaseModel):
    __tablename__ = 'knowledge_articles'
    
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    chatbot_id = db.Column(db.String(36), db.ForeignKey('chatbots.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.JSON, default=[])
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    chatbot = db.relationship('Chatbot', back_populates='knowledge_articles')
    
    def __repr__(self):
        return f'<KnowledgeArticle {self.title}>'

class FAQ(BaseModel):
    __tablename__ = 'faqs'
    
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    chatbot_id = db.Column(db.String(36), db.ForeignKey('chatbots.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    priority = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    chatbot = db.relationship('Chatbot', back_populates='faqs')
    
    def __repr__(self):
        return f'<FAQ {self.question[:50]}>'

