from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, SecurityScopes
from sqlalchemy.orm import Session

from src.api.schemas import UserCreate, UserLogin, Token
from src.config.auth_settings import auth_settings
from src.database.db import get_db
from src.exceptions.custom_exceptions import APIError
from src.repositories.user_repository import UserRepository


async def auth_get_current_user(
        security_scopes: SecurityScopes,
        credentials: HTTPAuthorizationCredentials,
        db: Session
):
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = UserRepository(db).get_user_by_username(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unexpected error during token validation: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.user_repo = UserRepository(db)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM)
        return encoded_jwt

    async def register(self, user_data: UserCreate) -> Token:
        try:
            existing_user = self.user_repo.get_user_by_username(user_data.username)
            if existing_user:
                raise APIError("Username already exists", status_code=400)
            user = self.user_repo.create_user(
                username=user_data.username,
                email=user_data.email,
                password=user_data.password
            )
            access_token = self.create_access_token(data={"sub": user.username})
            return Token(access_token=access_token, token_type="bearer")
        except APIError as e:
            raise e
        except Exception as e:
            raise APIError(f"Unexpected error during registration: {str(e)}")

    async def login(self, user_data: UserLogin) -> Token:
        try:
            user = self.user_repo.get_user_by_username(user_data.username)
            if not user or not self.user_repo.pwd_context.verify(user_data.password, user.hashed_password):
                raise APIError("Invalid username or password", status_code=401)
            access_token = self.create_access_token(data={"sub": user.username})
            return Token(access_token=access_token, token_type="bearer")
        except APIError as e:
            raise e
        except Exception as e:
            raise APIError(f"Unexpected error during login: {str(e)}")
