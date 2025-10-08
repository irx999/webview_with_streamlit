"""FastapiApp"""

from fastapi import APIRouter

from .pywebview import window

api_router = APIRouter()
api_router.include_router(window.router)


@api_router.get("/")
async def root():
    return {"message": "Hello ???!"}
