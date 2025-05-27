from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas import UserCreate, UserLogin, Token
from src.exceptions.custom_exceptions import APIError
from src.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, auth_service: AuthService = Depends()):
    try:
        return await auth_service.register(user_data)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, auth_service: AuthService = Depends()):
    try:
        return await auth_service.login(user_data)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
