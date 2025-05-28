from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.api.schemas import RestCountryResponse
from src.exceptions.custom_exceptions import DatabaseError
from src.repositories.country_repository import CountryRepository


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def country_repo(mock_db):
    return CountryRepository(db=mock_db)


def test_get_country_by_code_found(country_repo, mock_db):
    mock_country = MagicMock()
    mock_country.configure_mock(code="US", name="United States")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_country

    result = country_repo.get_country_by_code("US")
    assert result is not None
    assert result.code == "US"
    assert result.name == "United States"
    mock_db.query.assert_called_once()


def test_get_country_by_code_not_found(country_repo, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = country_repo.get_country_by_code("XX")
    assert result is None
    mock_db.query.assert_called_once()


def test_create_country_success(country_repo, mock_db):
    country_data = {
        "code": "US",
        "name": "United States",
        "full_name": "United States of America",
        "region": "Americas",
    }

    result = country_repo.create_country(**country_data)
    assert result is not None
    assert result.code == "US"
    assert result.name == "United States"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_country_database_error(country_repo, mock_db):
    country_data = {"code": "US", "name": "United States"}
    mock_db.commit.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(DatabaseError) as exc_info:
        country_repo.create_country(**country_data)
    assert "Database error while creating country: DB error" in str(exc_info.value)
    mock_db.add.assert_called_once()
    mock_db.rollback.assert_called_once()


def test_create_country_from_rest_success(country_repo, mock_db, mocker):
    mock_rest_country = MagicMock(spec=RestCountryResponse)
    country_data = {
        "code": "US",
        "name": "United States",
        "full_name": "United States of America",
        "region": "Americas",
    }
    mock_rest_country.to_country_data.return_value = country_data
    mock_country = MagicMock()
    mock_country.configure_mock(**country_data)
    mocker.patch.object(country_repo, "create_country", return_value=mock_country)

    result = country_repo.create_country_from_rest(mock_rest_country)
    assert result is not None
    assert result.code == "US"
    assert result.name == "United States"
    assert result.full_name == "United States of America"
    assert result.region == "Americas"
    country_repo.create_country.assert_called_once_with(**country_data)


def test_create_country_from_rest_database_error(country_repo, mock_db, mocker):
    mock_rest_country = MagicMock(spec=RestCountryResponse)
    mock_rest_country.to_country_data.return_value = {
        "code": "US",
        "name": "United States",
    }
    mocker.patch.object(
        country_repo, "create_country", side_effect=SQLAlchemyError("DB error")
    )

    with pytest.raises(DatabaseError) as exc_info:
        country_repo.create_country_from_rest(mock_rest_country)
    assert "Database error while mapping REST country data: DB error" in str(
        exc_info.value
    )


def test_create_country_from_rest_unexpected_error(country_repo, mock_db, mocker):
    mock_rest_country = MagicMock(spec=RestCountryResponse)
    mock_rest_country.to_country_data.side_effect = ValueError("Invalid data")

    with pytest.raises(DatabaseError) as exc_info:
        country_repo.create_country_from_rest(mock_rest_country)
    assert "Unexpected error while mapping REST country data: Invalid data" in str(
        exc_info.value
    )
