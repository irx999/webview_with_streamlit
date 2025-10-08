from fastapi import FastAPI

from .api.v1.main import api_router

app = FastAPI(
    root_path="/api/v1",
)


app.include_router(api_router)
