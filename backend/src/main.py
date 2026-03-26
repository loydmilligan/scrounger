from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .api import api_router

app = FastAPI(
    title="Scrounger",
    description="Secondary sales tracking for Reddit, eBay, Swappa, and more",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "scrounger"}


@app.get("/")
def root():
    return {
        "name": "Scrounger API",
        "version": "1.0.0",
        "description": "Secondary sales tracking"
    }


# Include API routes
app.include_router(api_router, prefix="/api")
