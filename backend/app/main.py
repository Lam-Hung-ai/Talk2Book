from fastapi import FastAPI
from app.core.config import settings
from starlette.middleware.cors import CORSMiddleware
from app.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/{settings.API_V1_STR}/openapi.json" # API_ENDPOINT: http://127.0.0.1:8000/docs  OPENAPI URL: http://127.0.0.1:8000/api/v1/openapi.json 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],         
    allow_headers=["*"], 
)

app.include_router(api_router, prefix="/api/v1")

# app.include_router()
@app.get("/")
async def root():
    return {
        "message": "Talk 2 Book Project"
    }