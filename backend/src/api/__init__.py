from fastapi import APIRouter
from .items import router as items_router
from .leads import router as leads_router
from .sales import router as sales_router
from .settings import router as settings_router
from .ai import router as ai_router
from .export import router as export_router
from .webhook import router as webhook_router
from .categories import router as categories_router
from .tags import router as tags_router
from .value_factors import router as value_factors_router
from .item_images import router as item_images_router
from .marketplace import router as marketplace_router

api_router = APIRouter()

api_router.include_router(items_router, prefix="/items", tags=["Items"])
api_router.include_router(leads_router, prefix="/leads", tags=["Leads"])
api_router.include_router(sales_router, prefix="/sales", tags=["Sales"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
api_router.include_router(export_router, prefix="/export", tags=["Export"])
api_router.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])
api_router.include_router(categories_router, prefix="/categories", tags=["Categories"])
api_router.include_router(tags_router, prefix="/tags", tags=["Tags"])
api_router.include_router(value_factors_router, prefix="/value-factors", tags=["Value Factors"])
api_router.include_router(item_images_router, prefix="/item-images", tags=["Item Images"])
api_router.include_router(marketplace_router, prefix="/marketplaces", tags=["Marketplaces"])
