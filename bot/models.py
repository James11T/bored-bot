from bot import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    """Represents a discord user"""
    __tablename__ = "user"
    id = Column(String(30), primary_key=True)
    level = Column(Integer, nullable=False, default=1)
    xp = Column(Integer, nullable=False, default=0)
    total_messages = Column(Integer, nullable=False, default=0)
    total_seconds = Column(Integer, nullable=False, default=0)
    background_image = Column(Integer, nullable=False, default=0)


class Server(Base):
    """Represents a discord server"""
    __tablename__ = "server"
    id = Column(String(30), primary_key=True)
    total_messages = Column(Integer, nullable=False, default=0)


class Membership(Base):
    """Represents the link between a discord user and a server"""
    __tablename__ = "membership"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(30), nullable=False)
    server_id = Column(String(30), nullable=False)
    messages_sent = Column(Integer, nullable=False, default=0)
    last_message = Column(Integer, nullable=False, default=0)
    voice_time = Column(Integer, nullable=False, default=0)
