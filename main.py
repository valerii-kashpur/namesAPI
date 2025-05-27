from fastapi import FastAPI

from src.api.routes import router

app = FastAPI(
    title="Name from country",
    description="Get country by name",
    version="0.1.0",
)

app.include_router(router)
