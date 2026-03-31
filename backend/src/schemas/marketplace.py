from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Marketplace Rules
class MarketplaceRuleBase(BaseModel):
    rule_type: str
    rule_text: str
    is_strict: bool = False
    example_good: Optional[str] = None
    example_bad: Optional[str] = None
    sort_order: int = 0


class MarketplaceRuleCreate(MarketplaceRuleBase):
    pass


class MarketplaceRuleUpdate(BaseModel):
    rule_type: Optional[str] = None
    rule_text: Optional[str] = None
    is_strict: Optional[bool] = None
    example_good: Optional[str] = None
    example_bad: Optional[str] = None
    sort_order: Optional[int] = None


class MarketplaceRuleResponse(MarketplaceRuleBase):
    id: int
    marketplace_id: int

    class Config:
        from_attributes = True


# Marketplace AI Prompts
class MarketplaceAIPromptBase(BaseModel):
    prompt_type: str
    prompt_template: str
    model_preference: Optional[str] = None
    notes: Optional[str] = None


class MarketplaceAIPromptCreate(MarketplaceAIPromptBase):
    pass


class MarketplaceAIPromptUpdate(BaseModel):
    prompt_type: Optional[str] = None
    prompt_template: Optional[str] = None
    model_preference: Optional[str] = None
    notes: Optional[str] = None


class MarketplaceAIPromptResponse(MarketplaceAIPromptBase):
    id: int
    marketplace_id: int

    class Config:
        from_attributes = True


# Marketplace
class MarketplaceBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    platform_type: str = "other"
    active: bool = True
    fee_percentage: float = 0.0
    fee_flat: float = 0.0
    fee_notes: Optional[str] = None
    feedback_timer_days: int = 3
    chaser_timer_days: int = 14
    bump_interval_hours: Optional[int] = None
    can_auto_bump: bool = False


class MarketplaceCreate(MarketplaceBase):
    pass


class MarketplaceUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    platform_type: Optional[str] = None
    active: Optional[bool] = None
    fee_percentage: Optional[float] = None
    fee_flat: Optional[float] = None
    fee_notes: Optional[str] = None
    feedback_timer_days: Optional[int] = None
    chaser_timer_days: Optional[int] = None
    bump_interval_hours: Optional[int] = None
    can_auto_bump: Optional[bool] = None


class MarketplaceResponse(MarketplaceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    rules: List[MarketplaceRuleResponse] = []
    ai_prompts: List[MarketplaceAIPromptResponse] = []

    class Config:
        from_attributes = True


class MarketplaceList(BaseModel):
    marketplaces: List[MarketplaceResponse]
    total: int


class MarketplaceRuleList(BaseModel):
    rules: List[MarketplaceRuleResponse]
    total: int


class MarketplaceAIPromptList(BaseModel):
    prompts: List[MarketplaceAIPromptResponse]
    total: int
