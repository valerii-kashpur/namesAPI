from fastapi import APIRouter

from src.api.routes.auth import router as auth
from src.api.routes.healthcheck import router as healthcheck
from src.api.routes.names import router as names
from src.api.routes.popular_names import router as popular_names

router = APIRouter()

router.include_router(healthcheck)
router.include_router(names)
router.include_router(popular_names)
router.include_router(auth)
