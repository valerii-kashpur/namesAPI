from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.exceptions.custom_exceptions import DatabaseError
from src.repositories.user_repository import UserRepository


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def user_repo(mock_db):
    return UserRepository(db=mock_db)


def test_get_user_by_username_found(user_repo, mock_db):
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.email = "test@example.com"
    mock_user.hashed_password = "hashed_password"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    result = user_repo.get_user_by_username("testuser")
    assert result is not None
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    mock_db.query.assert_called_once()


def test_get_user_by_username_not_found(user_repo, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = user_repo.get_user_by_username("nonexistent")
    assert result is None
    mock_db.query.assert_called_once()


def test_create_user_success(user_repo, mock_db, mocker):
    mocker.patch.object(user_repo.pwd_context, "hash", return_value="hashed_password")

    user = user_repo.create_user(
        username="newuser", email="new@example.com", password="password"
    )
    assert user is not None
    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert user.hashed_password == "hashed_password"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_user_database_error(user_repo, mock_db, mocker):
    mocker.patch.object(user_repo.pwd_context, "hash", return_value="hashed_password")
    mock_db.commit.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(DatabaseError) as exc_info:
        user_repo.create_user(
            username="newuser", email="new@example.com", password="password"
        )
    assert "Database error while creating user" in str(exc_info.value)
    mock_db.add.assert_called_once()
    mock_db.rollback.assert_called_once()
