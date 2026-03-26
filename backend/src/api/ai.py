from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import httpx

from ..database import get_db
from ..models import UserSetting, Item
from ..config import settings as app_settings

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048


class GeneratePostRequest(BaseModel):
    item_id: int
    platform: str = "reddit"
    subreddit: Optional[str] = "hardwareswap"


class PriceCheckRequest(BaseModel):
    item_name: str
    condition: Optional[str] = "good"
    description: Optional[str] = None


class ShippingHelpRequest(BaseModel):
    weight_lbs: float
    length_in: float
    width_in: float
    height_in: float
    from_zip: str
    to_zip: str


class ParseBundleRequest(BaseModel):
    url: str  # Reddit post URL
    create_items: bool = False  # Whether to auto-create items in the database


def get_api_key(db: Session) -> str:
    setting = db.query(UserSetting).filter(UserSetting.key == "openrouter_api_key").first()
    return setting.value if setting else app_settings.openrouter_api_key


def get_default_model(db: Session) -> str:
    setting = db.query(UserSetting).filter(UserSetting.key == "default_model").first()
    return setting.value if setting else app_settings.openrouter_model


@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """General AI chat endpoint."""
    api_key = get_api_key(db)
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenRouter API key not configured")

    model = request.model or get_default_model(db)

    messages = []
    if request.system_prompt:
        messages.append({"role": "system", "content": request.system_prompt})

    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

            return {
                "content": data["choices"][0]["message"]["content"],
                "model": data.get("model"),
                "usage": data.get("usage")
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")


@router.post("/generate-post")
async def generate_post(request: GeneratePostRequest, db: Session = Depends(get_db)):
    """Generate a sales post for an item."""
    api_key = get_api_key(db)
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenRouter API key not configured")

    item = db.query(Item).filter(Item.id == request.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if request.platform == "reddit":
        system_prompt = f"""You are an expert at writing sales posts for r/{request.subreddit}.
Follow the subreddit's standard format:
- Title should be: [STATE-ZIP] [H] Item Name [W] PayPal/Local Cash
- Include timestamps requirement mention
- List item condition clearly
- State asking price
- Mention shipping/local pickup options
- Be concise but informative

Generate a professional, honest listing that will attract buyers."""

        user_prompt = f"""Generate a sales post for:
Item: {item.name}
Description: {item.description or 'Not provided'}
Condition: {item.condition or 'Good'}
Asking Price: ${item.asking_price or 'Make offer'}
Category: {item.category or 'Electronics'}

Notes: {item.notes or 'None'}"""
    else:
        system_prompt = f"""You are an expert at writing sales listings for {request.platform}.
Create a compelling, honest listing that highlights the item's value."""

        user_prompt = f"""Generate a sales listing for:
Item: {item.name}
Description: {item.description or 'Not provided'}
Condition: {item.condition or 'Good'}
Asking Price: ${item.asking_price or 'Make offer'}"""

    model = get_default_model(db)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

            return {
                "post": data["choices"][0]["message"]["content"],
                "platform": request.platform,
                "item_name": item.name
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")


@router.post("/price-check")
async def price_check(request: PriceCheckRequest, db: Session = Depends(get_db)):
    """Get AI-assisted price suggestions for an item."""
    api_key = get_api_key(db)
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenRouter API key not configured")

    system_prompt = """You are an expert at pricing used electronics and tech items for resale.
Based on your knowledge of secondary markets like eBay, Reddit (hardwareswap, homelabsales),
Swappa, and OfferUp, provide realistic price suggestions.

Always provide:
1. A recommended price range (low - high)
2. Quick sale price (for fast turnover)
3. Patient seller price (if willing to wait)
4. Key factors affecting price
5. Tips for getting the best price

Be realistic and honest about pricing. Base your suggestions on actual market data."""

    user_prompt = f"""What should I price this item at?

Item: {request.item_name}
Condition: {request.condition}
Additional details: {request.description or 'None provided'}

Please provide pricing suggestions for secondary market sales."""

    model = get_default_model(db)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 1024
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

            return {
                "suggestions": data["choices"][0]["message"]["content"],
                "item_name": request.item_name
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")


@router.post("/shipping-help")
async def shipping_help(request: ShippingHelpRequest, db: Session = Depends(get_db)):
    """Get AI-assisted shipping cost estimates and tips."""
    api_key = get_api_key(db)
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenRouter API key not configured")

    system_prompt = """You are an expert at shipping packages for resale items.
Provide helpful shipping cost estimates and tips based on package dimensions and weight.

Include:
1. Estimated costs for major carriers (USPS, UPS, FedEx)
2. Recommended shipping method based on value/weight
3. Packaging tips to reduce costs
4. Insurance recommendations
5. Tracking requirements

Be practical and focus on cost-effective solutions."""

    user_prompt = f"""Help me figure out shipping for a package:

Dimensions: {request.length_in}" x {request.width_in}" x {request.height_in}"
Weight: {request.weight_lbs} lbs
From: {request.from_zip}
To: {request.to_zip}

What are my shipping options and estimated costs?"""

    model = get_default_model(db)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 1024
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

            return {
                "shipping_info": data["choices"][0]["message"]["content"],
                "dimensions": f"{request.length_in}x{request.width_in}x{request.height_in}",
                "weight": request.weight_lbs
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")


@router.post("/parse-bundle")
async def parse_bundle(request: ParseBundleRequest, db: Session = Depends(get_db)):
    """
    Parse a Reddit sales post to extract individual items from a bundle.
    Uses AI to identify separate items, their conditions, and estimated prices.
    """
    api_key = get_api_key(db)
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenRouter API key not configured")

    # Fetch the Reddit post
    url = request.url.rstrip("/")
    if not url.endswith(".json"):
        url += ".json"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"User-Agent": "Scrounger/1.0"},
                follow_redirects=True,
                timeout=30.0
            )
            response.raise_for_status()
            json_data = response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch Reddit post: {str(e)}")

    # Extract post content
    try:
        post_data = json_data[0]["data"]["children"][0]["data"]
        title = post_data.get("title", "")
        selftext = post_data.get("selftext", "")
        post_content = f"Title: {title}\n\nBody:\n{selftext}"
    except (KeyError, IndexError) as e:
        raise HTTPException(status_code=400, detail="Could not parse Reddit post structure")

    # Use AI to extract individual items
    system_prompt = """You are an expert at parsing sales posts from r/hardwareswap and r/homelabsales.
Your job is to identify individual items being sold in a bundle or multi-item listing.

For each item, extract:
1. Name/model of the item
2. Condition (new, like_new, good, fair, poor)
3. Asking price if mentioned (null if not specified or "bundled")
4. Brief description
5. Category (e.g., GPU, CPU, RAM, SSD, Network, Server, Accessory)

Output your response as a JSON array with this exact format:
[
  {
    "name": "Item name/model",
    "condition": "good",
    "asking_price": 150.00,
    "description": "Brief description",
    "category": "Category"
  }
]

If an item doesn't have a specific price (e.g., "bundle only" or price for whole lot), set asking_price to null.
Be thorough - identify ALL distinct items mentioned, even accessories.
Only output valid JSON, no additional text."""

    user_prompt = f"""Parse this Reddit sales post and extract all individual items:

{post_content}

Return a JSON array of all items found."""

    model = get_default_model(db)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2048
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Parse the JSON response
            import json
            # Clean up the response in case it has markdown code blocks
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            items = json.loads(content)

            # Optionally create items in the database
            created_items = []
            if request.create_items and isinstance(items, list):
                for item_data in items:
                    new_item = Item(
                        name=item_data.get("name", "Unknown Item"),
                        description=item_data.get("description", ""),
                        category=item_data.get("category", ""),
                        condition=item_data.get("condition", "good"),
                        asking_price=item_data.get("asking_price"),
                        status="draft",
                        platforms=["reddit"],
                        notes=f"Parsed from: {request.url}"
                    )
                    db.add(new_item)
                    db.flush()
                    created_items.append({
                        "id": new_item.id,
                        "name": new_item.name
                    })
                db.commit()

            return {
                "success": True,
                "post_title": title,
                "items_found": len(items) if isinstance(items, list) else 0,
                "items": items,
                "created_items": created_items if request.create_items else None,
                "source_url": request.url
            }

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {str(e)}")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")
