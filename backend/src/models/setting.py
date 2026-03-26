from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime
from datetime import datetime
from ..database import Base


class UserSetting(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(255), unique=True, nullable=False, index=True)
    nickname = Column(String(100), nullable=False)
    description = Column(Text)
    model_type = Column(String(50), default="general")  # general, coding, image, reasoning
    cost_tier = Column(String(10), default="$$")  # $, $$, $$$
    context_length = Column(Integer)
    supports_streaming = Column(Boolean, default=True)
    supports_reasoning = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    prompt_price = Column(Float)  # per 1M tokens
    completion_price = Column(Float)  # per 1M tokens
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
