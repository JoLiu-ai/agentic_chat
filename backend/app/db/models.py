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
    """消息模型 - 支持树形结构（父节点、子节点、兄弟节点）"""
    __tablename__ = 'messages'
    
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    agent_type = Column(String, nullable=True)
    model = Column(String, default='gpt-4o')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 树形结构字段
    parent_id = Column(Integer, ForeignKey('messages.message_id', ondelete='CASCADE'), nullable=True)
    sibling_index = Column(Integer, default=0)  # 同一父节点下的兄弟节点索引（从0开始）
    
    # Relationships
    session = relationship('Session', back_populates='messages')
    feedbacks = relationship('MessageFeedback', back_populates='message', cascade='all, delete-orphan')
    parent = relationship('Message', remote_side=[message_id], backref='children')


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


# class Document(Base):
#     """文档模型 - 存储上传的文档元数据"""
#     __tablename__ = 'documents'
    
#     doc_id = Column(String, primary_key=True)  # 文档唯一ID
#     user_id = Column(String, nullable=False, default='default_user', index=True)
#     file_name = Column(String, nullable=False)
#     file_path = Column(String, nullable=False)
#     file_size = Column(Integer)  # 文件大小（字节）
#     file_type = Column(String)  # .pdf, .md, .docx等
#     num_chunks = Column(Integer, default=0)  # 向量块数量
#     status = Column(String, default='processing')  # processing, completed, failed
#     error_message = Column(Text, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # 索引
#     __table_args__ = (
#         Index('idx_documents_user_created', 'user_id', 'created_at'),
#     )