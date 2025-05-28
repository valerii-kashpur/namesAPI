from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, SecurityScopes
from sqlalchemy.orm import Session

from src.api.schemas import UserCreate, UserLogin
from src.config.auth_settings import auth_settings
from src.services.auth_service import auth_get_current_user, AuthService
from src.utils.jwt import create_jwt_token


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_auth_settings(mocker):
    mocker.patch("src.config.auth_settings.auth_settings.SECRET_KEY", "test-secret-key")
    mocker.patch("src.config.auth_settings.auth_settings.ALGORITHM", "HS256")
    mocker.patch(
        "src.config.auth_settings.auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES", 30
    )
    return auth_settings


@pytest.fixture
def auth_service(mock_db, mock_auth_settings):
    return AuthService(db=mock_db)


def test_create_access_token(auth_service):
    data = {"sub": "testuser"}
    token = auth_service.create_access_token(data)
    assert token is not None
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_register_success(auth_service, mocker):
    user_data = UserCreate(
        username="newuser", email="new@example.com", password="password"
    )
    mocker.patch.object(
        auth_service.user_repo, "get_user_by_username", return_value=None
    )
    mocker.patch.object(
        auth_service.user_repo,
        "create_user",
        return_value=MagicMock(username="newuser"),
    )

    token = await auth_service.register(user_data)
    assert token.access_token is not None
    assert token.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_success(auth_service, mocker):
    user_data = UserLogin(username="testuser", password="password")
    mock_user = MagicMock(
        username="testuser",
        hashed_password=auth_service.user_repo.pwd_context.hash("password"),
    )
    mocker.patch.object(
        auth_service.user_repo, "get_user_by_username", return_value=mock_user
    )

    token = await auth_service.login(user_data)
    assert token.access_token is not None
    assert token.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(auth_service, mocker):
    user_data = UserLogin(username="testuser", password="wrongpassword")
    mock_user = MagicMock(
        username="testuser",
        hashed_password=auth_service.user_repo.pwd_context.hash("password"),
    )
    mocker.patch.object(
        auth_service.user_repo, "get_user_by_username", return_value=mock_user
    )

    with pytest.raises(Exception) as exc_info:
        await auth_service.login(user_data)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_auth_get_current_user_success(mock_db, mock_auth_settings, mocker):
    token = create_jwt_token({"sub": "testuser"}, "test-secret-key", "HS256", 30)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    security_scopes = SecurityScopes()
    mocker.patch(
        "src.repositories.user_repository.UserRepository.get_user_by_username",
        return_value=MagicMock(username="testuser"),
    )

    user = await auth_get_current_user(security_scopes, credentials, mock_db)
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_auth_get_current_user_invalid_token(mock_db, mock_auth_settings):
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="invalidtoken"
    )
    security_scopes = SecurityScopes()

    with pytest.raises(HTTPException) as exc_info:
        await auth_get_current_user(security_scopes, credentials, mock_db)
    assert exc_info.value.status_code == 401
