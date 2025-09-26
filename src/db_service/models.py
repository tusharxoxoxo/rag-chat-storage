from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    is_favorite = Column(Boolean, default=False)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False)
    sender = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(Text)

    session = relationship('ChatSession')

# Database engine factory
def get_engine(url):
    return create_engine(url)