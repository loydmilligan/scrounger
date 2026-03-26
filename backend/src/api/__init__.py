from fastapi import APIRouter
from .items import router as items_router
from .leads import router as leads_router
from .sales import router as sales_router
from .settings import router as settings_router
from .ai import router as ai_router
from .export import router as export_router
from .webhook import router as webhook_router

api_router = APIRouter()

api_router.include_router(items_router, prefix="/items", tags=["Items"])
api_router.include_router(leads_router, prefix="/leads", tags=["Leads"])
api_router.include_router(sales_router, prefix="/sales", tags=["Sales"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
api_router.include_router(export_router, prefix="/export", tags=["Export"])
api_router.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])
