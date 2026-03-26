from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import httpx

from ..database import get_db
from ..models import UserSetting, AIModel
from ..schemas import AISettings, AIModelCreate, AIModelUpdate, AIModelResponse
from ..config import settings as app_settings

router = APIRouter()


def get_setting(db: Session, key: str) -> str | None:
    setting = db.query(UserSetting).filter(UserSetting.key == key).first()
    return setting.value if setting else None


def set_setting(db: Session, key: str, value: str):
    setting = db.query(UserSetting).filter(UserSetting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = UserSetting(key=key, value=value)
        db.add(setting)
    db.commit()


@router.get("/ai", response_model=AISettings)
def get_ai_settings(db: Session = Depends(get_db)):
    api_key = get_setting(db, "openrouter_api_key") or app_settings.openrouter_api_key
    default_model = get_setting(db, "default_model") or app_settings.openrouter_model

    return AISettings(
        openrouter_api_key="",  # Never return actual key
        has_api_key=bool(api_key),
        default_model=default_model
    )


@router.put("/ai", response_model=AISettings)
def update_ai_settings(settings_data: AISettings, db: Session = Depends(get_db)):
    if settings_data.openrouter_api_key:
        set_setting(db, "openrouter_api_key", settings_data.openrouter_api_key)

    if settings_data.default_model:
        set_setting(db, "default_model", settings_data.default_model)

    api_key = get_setting(db, "openrouter_api_key") or app_settings.openrouter_api_key

    return AISettings(
        openrouter_api_key="",
        has_api_key=bool(api_key),
        default_model=settings_data.default_model
    )


@router.post("/ai/test")
async def test_ai_connection(db: Session = Depends(get_db)):
    api_key = get_setting(db, "openrouter_api_key") or app_settings.openrouter_api_key

    if not api_key:
        return {"success": False, "message": "No API key configured"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )

            if response.status_code == 200:
                return {"success": True, "message": "Connection successful"}
            elif response.status_code == 401:
                return {"success": False, "message": "Invalid API key"}
            else:
                return {"success": False, "message": f"API error: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}


# AI Models CRUD
@router.get("/ai-models", response_model=List[AIModelResponse])
def list_ai_models(db: Session = Depends(get_db)):
    models = db.query(AIModel).order_by(AIModel.is_favorite.desc(), AIModel.nickname).all()
    return models


@router.post("/ai-models", response_model=AIModelResponse)
def create_ai_model(model_data: AIModelCreate, db: Session = Depends(get_db)):
    existing = db.query(AIModel).filter(AIModel.model_id == model_data.model_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Model already exists")

    model = AIModel(**model_data.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@router.get("/ai-models/lookup/{model_id:path}")
async def lookup_model(model_id: str, db: Session = Depends(get_db)):
    """Look up model details from OpenRouter API."""
    api_key = get_setting(db, "openrouter_api_key") or app_settings.openrouter_api_key

    if not api_key:
        raise HTTPException(status_code=400, detail="No API key configured")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            for model in data.get("data", []):
                if model.get("id") == model_id:
                    # Determine cost tier
                    prompt_price = float(model.get("pricing", {}).get("prompt", 0)) * 1000000
                    if prompt_price < 1:
                        cost_tier = "$"
                    elif prompt_price < 10:
                        cost_tier = "$$"
                    else:
                        cost_tier = "$$$"

                    return {
                        "model_id": model["id"],
                        "nickname": model.get("name", model["id"].split("/")[-1]),
                        "description": model.get("description", ""),
                        "context_length": model.get("context_length"),
                        "cost_tier": cost_tier,
                        "prompt_price": prompt_price,
                        "completion_price": float(model.get("pricing", {}).get("completion", 0)) * 1000000,
                        "supports_streaming": True,  # Most do
                        "supports_reasoning": "reason" in model["id"].lower() or "think" in model["id"].lower()
                    }

            raise HTTPException(status_code=404, detail="Model not found")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"API error: {str(e)}")


@router.patch("/ai-models/{model_id}", response_model=AIModelResponse)
def update_ai_model(model_id: int, model_data: AIModelUpdate, db: Session = Depends(get_db)):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    update_data = model_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(model, key, value)

    db.commit()
    db.refresh(model)
    return model


@router.delete("/ai-models/{model_id}")
def delete_ai_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    db.delete(model)
    db.commit()
    return {"message": "Model deleted successfully"}


@router.post("/ai-models/{model_id}/favorite")
def toggle_favorite(model_id: int, db: Session = Depends(get_db)):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    model.is_favorite = not model.is_favorite
    db.commit()
    return {"is_favorite": model.is_favorite}
