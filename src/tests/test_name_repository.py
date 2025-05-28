from datetime import datetime, timedelta, UTC
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import OperationalError

from src.exceptions.custom_exceptions import DatabaseError
from src.repositories.name_repository import NameRepository


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def name_repo(mock_db):
    return NameRepository(db=mock_db)


def test_get_or_create_name_existing(name_repo, mock_db):
    mock_name = MagicMock()
    mock_name.configure_mock(
        name="john", count_of_requests=5, last_accessed_at=datetime.now(UTC)
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_name

    result = name_repo.get_or_create_name("John")
    assert result.name == "john"
    assert result.count_of_requests == 6
    mock_db.commit.assert_called_once()


def test_get_or_create_name_new(name_repo, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = name_repo.get_or_create_name("Jane")
    assert result.name == "Jane"
    assert result.count_of_requests == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_get_name_countries_recent(name_repo, mock_db):
    mock_name = MagicMock()
    mock_name.configure_mock(id=1, last_accessed_at=datetime.now(UTC))
    mock_name_country = MagicMock(name_id=1, country_id=1, probability=0.9)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_name
    mock_db.query.return_value.filter.return_value.all.return_value = [
        mock_name_country
    ]

    result = name_repo.get_name_countries("John", 1)
    assert len(result) == 1
    assert result[0].name_id == 1
    assert result[0].probability == 0.9


def test_get_name_countries_outdated(name_repo, mock_db):
    mock_name = MagicMock()
    mock_name.configure_mock(
        id=1, last_accessed_at=datetime.now(UTC) - timedelta(days=2)
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_name

    result = name_repo.get_name_countries("John", 1)
    assert len(result) == 0


def test_get_name_countries_no_name(name_repo, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = name_repo.get_name_countries("John", 1)
    assert len(result) == 0


def test_add_name_country(name_repo, mock_db):
    name_repo.add_name_country("John", "US", 0.9)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_get_popular_names_by_country_success(name_repo, mock_db):
    mock_name1 = MagicMock()
    mock_name1.configure_mock(name="John", count_of_requests=100)
    mock_name2 = MagicMock()
    mock_name2.configure_mock(name="Jane", count_of_requests=50)
    mock_query = mock_db.query.return_value
    mock_query.join.return_value.join.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
        mock_name1,
        mock_name2,
    ]

    result = name_repo.get_popular_names_by_country("US")
    assert len(result) == 2
    assert result[0].name == "John"
    assert result[0].count_of_requests == 100
    assert result[1].name == "Jane"


def test_get_popular_names_by_country_database_error(name_repo, mock_db):
    mock_query = mock_db.query.return_value
    mock_query.join.return_value.join.return_value.filter.return_value.order_by.return_value.limit.return_value.all.side_effect = OperationalError(
        statement="SELECT error", params=None, orig=Exception("Database error")
    )

    with pytest.raises(DatabaseError) as exc_info:
        name_repo.get_popular_names_by_country("US")
    assert (
        "Database error while fetching popular names for country US: (builtins.Exception) Database error"
        in str(exc_info.value)
    )
