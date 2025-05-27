from fastapi import APIRouter

from src.api.routes.healthcheck import router as healthcheck
from src.api.routes.names import router as names

router = APIRouter()

router.include_router(healthcheck)
router.include_router(names)
