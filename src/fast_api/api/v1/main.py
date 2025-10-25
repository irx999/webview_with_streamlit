"""FastapiApp"""

from fastapi import APIRouter

from .pywebview import window, clodop

api_router = APIRouter()
api_router.include_router(window.router)
api_router.include_router(clodop.router)


@api_router.get("/")
async def root():
    return {"message": "Hello ???!"}