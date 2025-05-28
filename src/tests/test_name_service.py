from unittest.mock import MagicMock, AsyncMock

import pytest

from src.api.schemas import NameCountryResponse, PopularNameResponse
from src.exceptions.custom_exceptions import APIError
from src.services.name_service import NameService


@pytest.fixture
def mock_nationalize_client():
    return AsyncMock()


@pytest.fixture
def mock_rest_countries_client():
    return AsyncMock()


@pytest.fixture
def mock_name_repo():
    return MagicMock()


@pytest.fixture
def mock_country_repo():
    return MagicMock()


@pytest.fixture
def name_service(mock_nationalize_client, mock_rest_countries_client, mock_name_repo, mock_country_repo):
    return NameService(
        nationalize_client=mock_nationalize_client,
        rest_countries_client=mock_rest_countries_client,
        name_repo=mock_name_repo,
        country_repo=mock_country_repo
    )


@pytest.mark.asyncio
async def test_get_countries_by_name_cached(name_service, mock_name_repo, mock_country_repo):
    mock_name = MagicMock()
    mock_name.id = 1
    mock_name.name = "John"
    mock_country = MagicMock()
    mock_country.configure_mock(
        id=1, code="US", name="USA", full_name="United States", region="Americas",
        subregion="North America", independent=True, google_maps_url="https://maps.google.com",
        open_street_map_url="https://openstreetmap.org", capital_name="Washington",
        capital_latitude=38.9, capital_longitude=-77.0, flag_png_url="flag.png",
        flag_svg_url="flag.svg", flag_alt="US flag", coat_of_arms_png_url="coa.png",
        coat_of_arms_svg_url="coa.svg", borders="CA,MX"
    )
    mock_name_country = MagicMock()
    mock_name_country.name_id = 1
    mock_name_country.country = mock_country
    mock_name_country.probability = 0.9
    mock_name_repo.get_or_create_name.return_value = mock_name
    mock_name_repo.get_name_countries.return_value = [mock_name_country]

    result = await name_service.get_countries_by_name("John", days_threshold=1)
    assert len(result) == 1
    assert isinstance(result[0], NameCountryResponse)
    assert result[0].name == "John"
    assert result[0].probability == 0.9
    assert result[0].country.name == "USA"


@pytest.mark.asyncio
async def test_get_countries_by_name_api(name_service, mock_name_repo, mock_rest_countries_client, mock_country_repo):
    mock_name = MagicMock()
    mock_name.id = 1
    mock_name.name = "John"
    mock_name_repo.get_or_create_name.return_value = mock_name
    mock_name_repo.get_name_countries.return_value = []
    name_service.nationalize_client.get_countries_by_name.return_value = {
        "country": [{"country_id": "US", "probability": 0.9}]
    }
    mock_country_repo.get_country_by_code.return_value = None
    mock_rest_countries_client.get_country_by_code.return_value = {
        "name": {"common": "USA"}, "region": "Americas", "subregion": "North America",
        "independent": True, "capital": ["Washington"], "latlng": [38.9, -77.0],
        "flags": {"png": "flag.png", "svg": "flag.svg", "alt": "US flag"},
        "coatOfArms": {"png": "coa.png", "svg": "coa.svg"}, "borders": ["CA", "MX"],
        "maps": {"googleMaps": "https://maps.google.com", "openStreetMaps": "https://openstreetmap.org"},
        "capitalInfo": {"latlng": [38.9, -77.0]}
    }
    mock_country = MagicMock()
    mock_country.configure_mock(
        id=1, code="US", name="USA", full_name="United States", region="Americas",
        subregion="North America", independent=True, google_maps_url="https://maps.google.com",
        open_street_map_url="https://openstreetmap.org", capital_name="Washington",
        capital_latitude=38.9, capital_longitude=-77.0, flag_png_url="flag.png",
        flag_svg_url="flag.svg", flag_alt="US flag", coat_of_arms_png_url="coa.png",
        coat_of_arms_svg_url="coa.svg", borders="CA,MX"
    )
    mock_country_repo.create_country_from_rest.return_value = mock_country

    result = await name_service.get_countries_by_name("John")
    assert len(result) == 1
    assert isinstance(result[0], NameCountryResponse)
    assert result[0].name == "John"
    assert result[0].probability == 0.9
    assert result[0].country.name == "USA"
    mock_name_repo.add_name_country.assert_called_once()


@pytest.mark.asyncio
async def test_get_countries_by_name_empty(name_service, mock_name_repo):
    mock_name = MagicMock()
    mock_name.id = 1
    mock_name.name = "John"
    mock_name_repo.get_or_create_name.return_value = mock_name
    mock_name_repo.get_name_countries.return_value = []
    name_service.nationalize_client.get_countries_by_name.return_value = {"country": []}

    result = await name_service.get_countries_by_name("John")
    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_popular_names_by_country_success(name_service, mock_country_repo, mock_name_repo):
    mock_country = MagicMock()
    mock_country.configure_mock(id=1, code="US", name="USA")
    mock_name1 = MagicMock()
    mock_name1.name = "John"
    mock_name1.count_of_requests = 100
    mock_name2 = MagicMock()
    mock_name2.name = "Jane"
    mock_name2.count_of_requests = 50
    mock_name_repo.get_popular_names_by_country.return_value = [mock_name1, mock_name2]
    mock_country_repo.get_country_by_code.return_value = mock_country

    result = await name_service.get_popular_names_by_country("US")
    assert len(result) == 2
    assert isinstance(result[0], PopularNameResponse)
    assert result[0].name == "John"
    assert result[0].count_of_requests == 100
    assert result[1].name == "Jane"


@pytest.mark.asyncio
async def test_get_popular_names_by_country_not_found(name_service, mock_country_repo):
    mock_country_repo.get_country_by_code.return_value = None

    with pytest.raises(APIError) as exc_info:
        await name_service.get_popular_names_by_country("XX")
    assert exc_info.value.status_code == 502
    assert "Country code XX not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_popular_names_by_country_empty(name_service, mock_country_repo, mock_name_repo):
    mock_country = MagicMock()
    mock_country.configure_mock(id=1, code="US", name="USA")
    mock_country_repo.get_country_by_code.return_value = mock_country
    mock_name_repo.get_popular_names_by_country.return_value = []

    result = await name_service.get_popular_names_by_country("US")
    assert len(result) == 0
