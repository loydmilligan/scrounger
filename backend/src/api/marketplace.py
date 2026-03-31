from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Marketplace, MarketplaceRule, MarketplaceAIPrompt, PlatformType, RuleType, PromptType
from ..schemas.marketplace import (
    MarketplaceCreate, MarketplaceUpdate, MarketplaceResponse, MarketplaceList,
    MarketplaceRuleCreate, MarketplaceRuleUpdate, MarketplaceRuleResponse, MarketplaceRuleList,
    MarketplaceAIPromptCreate, MarketplaceAIPromptUpdate, MarketplaceAIPromptResponse, MarketplaceAIPromptList
)

router = APIRouter()


# ============ Marketplace CRUD ============

@router.get("", response_model=MarketplaceList)
def list_marketplaces(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    platform_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all marketplaces, optionally filtered."""
    query = db.query(Marketplace).order_by(Marketplace.display_name, Marketplace.name)

    if active_only:
        query = query.filter(Marketplace.active == True)

    if platform_type:
        try:
            pt = PlatformType(platform_type)
            query = query.filter(Marketplace.platform_type == pt)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform type. Allowed: {[t.value for t in PlatformType]}"
            )

    total = query.count()
    marketplaces = query.offset(skip).limit(limit).all()

    return MarketplaceList(
        marketplaces=[_marketplace_to_response(m) for m in marketplaces],
        total=total
    )


@router.get("/{marketplace_id}", response_model=MarketplaceResponse)
def get_marketplace(marketplace_id: int, db: Session = Depends(get_db)):
    """Get a specific marketplace by ID."""
    marketplace = db.query(Marketplace).filter(Marketplace.id == marketplace_id).first()
    if not marketplace:
        raise HTTPException(status_code=404, detail="Marketplace not found")

    return _marketplace_to_response(marketplace)


@router.post("", response_model=MarketplaceResponse)
def create_marketplace(marketplace_data: MarketplaceCreate, db: Session = Depends(get_db)):
    """Create a new marketplace."""
    # Check if name already exists
    existing = db.query(Marketplace).filter(Marketplace.name == marketplace_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Marketplace with this name already exists")

    # Validate platform type
    data = marketplace_data.model_dump()
    try:
        data["platform_type"] = PlatformType(data["platform_type"])
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform type. Allowed: {[t.value for t in PlatformType]}"
        )

    marketplace = Marketplace(**data)
    db.add(marketplace)
    db.commit()
    db.refresh(marketplace)

    return _marketplace_to_response(marketplace)


@router.patch("/{marketplace_id}", response_model=MarketplaceResponse)
def update_marketplace(
    marketplace_id: int,
    marketplace_data: MarketplaceUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing marketplace."""
    marketplace = db.query(Marketplace).filter(Marketplace.id == marketplace_id).first()
    if not marketplace:
        raise HTTPException(status_code=404, detail="Marketplace not found")

    update_data = marketplace_data.model_dump(exclude_unset=True)

    # Check name uniqueness if being updated
    if "name" in update_data and update_data["name"] != marketplace.name:
        existing = db.query(Marketplace).filter(
            Marketplace.name == update_data["name"],
            Marketplace.id != marketplace_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Marketplace with this name already exists")

    # Validate platform type if provided
    if "platform_type" in update_data:
        try:
            update_data["platform_type"] = PlatformType(update_data["platform_type"])
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform type. Allowed: {[t.value for t in PlatformType]}"
            )

    for key, value in update_data.items():
        setattr(marketplace, key, value)

    db.commit()
    db.refresh(marketplace)

    return _marketplace_to_response(marketplace)


@router.delete("/{marketplace_id}")
def delete_marketplace(marketplace_id: int, db: Session = Depends(get_db)):
    """Delete a marketplace and all its rules/prompts."""
    marketplace = db.query(Marketplace).filter(Marketplace.id == marketplace_id).first()
    if not marketplace:
        raise HTTPException(status_code=404, detail="Marketplace not found")

    db.delete(marketplace)
    db.commit()
    return {"message": "Marketplace deleted successfully"}


# ============ Marketplace Rules CRUD ============

@router.get("/{marketplace_id}/rules", response_model=MarketplaceRuleList)
def list_marketplace_rules(
    marketplace_id: int,
    rule_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all rules for a marketplace."""
    marketplace = db.query(Marketplace).filter(Marketplace.id == marketplace_id).first()
    if not marketplace:
        raise HTTPException(status_code=404, detail="Marketplace not found")

    query = db.query(MarketplaceRule).filter(
        MarketplaceRule.marketplace_id == marketplace_id
    ).order_by(MarketplaceRule.sort_order, MarketplaceRule.id)

    if rule_type:
        try:
            rt = RuleType(rule_type)
            query = query.filter(MarketplaceRule.rule_type == rt)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid rule type. Allowed: {[t.value for t in RuleType]}"
            )

    rules = query.all()

    return MarketplaceRuleList(
        rules=[_rule_to_response(r) for r in rules],
        total=len(rules)
    )


@router.post("/{marketplace_id}/rules", response_model=MarketplaceRuleResponse)
def create_marketplace_rule(
    marketplace_id: int,
    rule_data: MarketplaceRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new rule for a marketplace."""
    marketplace = db.query(Marketplace).filter(Marketplace.id == marketplace_id).first()
    if not marketplace:
        raise HTTPException(status_code=404, detail="Marketplace not found")

    data = rule_data.model_dump()
    try:
        data["rule_type"] = RuleType(data["rule_type"])
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid rule type. Allowed: {[t.value for t in RuleType]}"
        )

    rule = MarketplaceRule(marketplace_id=marketplace_id, **data)
    db.add(rule)
    db.commit()
    db.refresh(rule)

    return _rule_to_response(rule)


@router.patch("/{marketplace_id}/rules/{rule_id}", response_model=MarketplaceRuleResponse)
def update_marketplace_rule(
    marketplace_id: int,
    rule_id: int,
    rule_data: MarketplaceRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing marketplace rule."""
    rule = db.query(MarketplaceRule).filter(
        MarketplaceRule.id == rule_id,
        MarketplaceRule.marketplace_id == marketplace_id
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = rule_data.model_dump(exclude_unset=True)

    if "rule_type" in update_data:
        try:
            update_data["rule_type"] = RuleType(update_data["rule_type"])
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid rule type. Allowed: {[t.value for t in RuleType]}"
            )

    for key, value in update_data.items():
        setattr(rule, key, value)

    db.commit()
    db.refresh(rule)

    return _rule_to_response(rule)


@router.delete("/{marketplace_id}/rules/{rule_id}")
def delete_marketplace_rule(
    marketplace_id: int,
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Delete a marketplace rule."""
    rule = db.query(MarketplaceRule).filter(
        MarketplaceRule.id == rule_id,
        MarketplaceRule.marketplace_id == marketplace_id
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully"}


# ============ Marketplace AI Prompts CRUD ============

@router.get("/{marketplace_id}/prompts", response_model=MarketplaceAIPromptList)
def list_marketplace_prompts(
    marketplace_id: int,
    prompt_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all AI prompts for a marketplace."""
    marketplace = db.query(Marketplace).filter(Marketplace.id == marketplace_id).first()
    if not marketplace:
        raise HTTPException(status_code=404, detail="Marketplace not found")

    query = db.query(MarketplaceAIPrompt).filter(
        MarketplaceAIPrompt.marketplace_id == marketplace_id
    ).order_by(MarketplaceAIPrompt.prompt_type, MarketplaceAIPrompt.id)

    if prompt_type:
        try:
            pt = PromptType(prompt_type)
            query = query.filter(MarketplaceAIPrompt.prompt_type == pt)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid prompt type. Allowed: {[t.value for t in PromptType]}"
            )

    prompts = query.all()

    return MarketplaceAIPromptList(
        prompts=[_prompt_to_response(p) for p in prompts],
        total=len(prompts)
    )


@router.post("/{marketplace_id}/prompts", response_model=MarketplaceAIPromptResponse)
def create_marketplace_prompt(
    marketplace_id: int,
    prompt_data: MarketplaceAIPromptCreate,
    db: Session = Depends(get_db)
):
    """Create a new AI prompt for a marketplace."""
    marketplace = db.query(Marketplace).filter(Marketplace.id == marketplace_id).first()
    if not marketplace:
        raise HTTPException(status_code=404, detail="Marketplace not found")

    data = prompt_data.model_dump()
    try:
        data["prompt_type"] = PromptType(data["prompt_type"])
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prompt type. Allowed: {[t.value for t in PromptType]}"
        )

    prompt = MarketplaceAIPrompt(marketplace_id=marketplace_id, **data)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    return _prompt_to_response(prompt)


@router.patch("/{marketplace_id}/prompts/{prompt_id}", response_model=MarketplaceAIPromptResponse)
def update_marketplace_prompt(
    marketplace_id: int,
    prompt_id: int,
    prompt_data: MarketplaceAIPromptUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing AI prompt."""
    prompt = db.query(MarketplaceAIPrompt).filter(
        MarketplaceAIPrompt.id == prompt_id,
        MarketplaceAIPrompt.marketplace_id == marketplace_id
    ).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    update_data = prompt_data.model_dump(exclude_unset=True)

    if "prompt_type" in update_data:
        try:
            update_data["prompt_type"] = PromptType(update_data["prompt_type"])
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid prompt type. Allowed: {[t.value for t in PromptType]}"
            )

    for key, value in update_data.items():
        setattr(prompt, key, value)

    db.commit()
    db.refresh(prompt)

    return _prompt_to_response(prompt)


@router.delete("/{marketplace_id}/prompts/{prompt_id}")
def delete_marketplace_prompt(
    marketplace_id: int,
    prompt_id: int,
    db: Session = Depends(get_db)
):
    """Delete an AI prompt."""
    prompt = db.query(MarketplaceAIPrompt).filter(
        MarketplaceAIPrompt.id == prompt_id,
        MarketplaceAIPrompt.marketplace_id == marketplace_id
    ).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    db.delete(prompt)
    db.commit()
    return {"message": "Prompt deleted successfully"}


# ============ Helper Functions ============

def _marketplace_to_response(marketplace: Marketplace) -> MarketplaceResponse:
    """Convert Marketplace model to response schema."""
    return MarketplaceResponse(
        id=marketplace.id,
        name=marketplace.name,
        display_name=marketplace.display_name,
        platform_type=marketplace.platform_type.value if marketplace.platform_type else "other",
        active=marketplace.active,
        fee_percentage=float(marketplace.fee_percentage) if marketplace.fee_percentage else 0.0,
        fee_flat=float(marketplace.fee_flat) if marketplace.fee_flat else 0.0,
        fee_notes=marketplace.fee_notes,
        feedback_timer_days=marketplace.feedback_timer_days,
        chaser_timer_days=marketplace.chaser_timer_days,
        bump_interval_hours=marketplace.bump_interval_hours,
        can_auto_bump=marketplace.can_auto_bump,
        created_at=marketplace.created_at,
        updated_at=marketplace.updated_at,
        rules=[_rule_to_response(r) for r in marketplace.rules],
        ai_prompts=[_prompt_to_response(p) for p in marketplace.ai_prompts]
    )


def _rule_to_response(rule: MarketplaceRule) -> MarketplaceRuleResponse:
    """Convert MarketplaceRule model to response schema."""
    return MarketplaceRuleResponse(
        id=rule.id,
        marketplace_id=rule.marketplace_id,
        rule_type=rule.rule_type.value if rule.rule_type else "general",
        rule_text=rule.rule_text,
        is_strict=rule.is_strict,
        example_good=rule.example_good,
        example_bad=rule.example_bad,
        sort_order=rule.sort_order
    )


def _prompt_to_response(prompt: MarketplaceAIPrompt) -> MarketplaceAIPromptResponse:
    """Convert MarketplaceAIPrompt model to response schema."""
    return MarketplaceAIPromptResponse(
        id=prompt.id,
        marketplace_id=prompt.marketplace_id,
        prompt_type=prompt.prompt_type.value if prompt.prompt_type else "body",
        prompt_template=prompt.prompt_template,
        model_preference=prompt.model_preference,
        notes=prompt.notes
    )
