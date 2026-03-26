from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AISettings(BaseModel):
    openrouter_api_key: Optional[str] = ""
    has_api_key: bool = False
    default_model: str = "anthropic/claude-3.5-sonnet"


class AIModelBase(BaseModel):
    model_id: str
    nickname: str
    description: Optional[str] = None
    model_type: Optional[str] = "general"
    cost_tier: Optional[str] = "$$"
    context_length: Optional[int] = None
    supports_streaming: Optional[bool] = True
    supports_reasoning: Optional[bool] = False
    is_favorite: Optional[bool] = False
    prompt_price: Optional[float] = None
    completion_price: Optional[float] = None


class AIModelCreate(AIModelBase):
    pass


class AIModelUpdate(BaseModel):
    nickname: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[str] = None
    cost_tier: Optional[str] = None
    context_length: Optional[int] = None
    supports_streaming: Optional[bool] = None
    supports_reasoning: Optional[bool] = None
    is_favorite: Optional[bool] = None
    prompt_price: Optional[float] = None
    completion_price: Optional[float] = None


class AIModelResponse(AIModelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
