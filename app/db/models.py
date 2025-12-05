"""
SQLAlchemy Models for Agentic Chat
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Session(Base):
    """会话模型"""
    __tablename__ = 'sessions'
    
    session_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, default='default_user')
    title = Column(String, default='新对话')
    project_id = Column(String, ForeignKey('projects.project_id'), nullable=True)
    is_starred = Column(Boolean, default=False)
    tags = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - use passive_deletes to let database handle cascade
    messages = relationship('Message', back_populates='session', cascade='all, delete', passive_deletes=True)
    project = relationship('Project', back_populates='sessions')


class Message(Base):
    """消息模型"""
    __tablename__ = 'messages'
    
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    agent_type = Column(String, nullable=True)
    model = Column(String, default='gpt-4o')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship('Session', back_populates='messages')
    feedbacks = relationship('MessageFeedback', back_populates='message', cascade='all, delete-orphan')


class Project(Base):
    """项目模型"""
    __tablename__ = 'projects'
    
    project_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, default='blue')
    icon = Column(String, default='📁')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship('Session', back_populates='project')


class MessageFeedback(Base):
    """消息反馈模型"""
    __tablename__ = 'message_feedback'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('messages.message_id', ondelete='CASCADE'), nullable=False)
    feedback_type = Column(String, nullable=False)  # 'like' or 'dislike'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship('Message', back_populates='feedbacks')
