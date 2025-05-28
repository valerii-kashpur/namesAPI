from typing import List

from src.api.schemas import NameCountryResponse, CountryDTO, RestCountryResponse, PopularNameResponse
from src.clients.nationalize import NationalizeClientInterface
from src.clients.rest_countries import RestCountriesClientInterface
from src.exceptions.custom_exceptions import APIError, DatabaseError
from src.exceptions.exception_handlers import handle_api_error, handle_database_error
from src.repositories.country_repository import CountryRepository
from src.repositories.name_repository import NameRepository


class NameService:
    def __init__(
            self,
            nationalize_client: NationalizeClientInterface,
            rest_countries_client: RestCountriesClientInterface,
            name_repo: NameRepository,
            country_repo: CountryRepository
    ):
        self.nationalize_client = nationalize_client
        self.rest_countries_client = rest_countries_client
        self.name_repo = name_repo
        self.country_repo = country_repo

    async def get_countries_by_name(self, name: str, days_threshold: int = 1) -> List[NameCountryResponse]:
        try:
            name_record = self.name_repo.get_or_create_name(name)
            cached_countries = self.name_repo.get_name_countries(name_record.id, days_threshold)
            if cached_countries:
                return [
                    NameCountryResponse(
                        name=name,
                        country=CountryDTO.from_orm(nc.country),
                        probability=nc.probability
                    ) for nc in cached_countries
                ]

            response = await self.nationalize_client.get_countries_by_name(name)
            if not response.get("country"):
                return []

            result = []
            for country_data in response["country"]:
                country_code = country_data["country_id"]
                probability = country_data["probability"]

                country = self.country_repo.get_country_by_code(country_code)
                if not country:
                    country_info = await self.rest_countries_client.get_country_by_code(country_code)
                    if not country_info:
                        raise APIError(f"Failed to fetch country data for code {country_code}")
                    if isinstance(country_info, list) and country_info:
                        country_info = country_info[0]
                    rest_country = RestCountryResponse(**country_info, code=country_code)
                    country = self.country_repo.create_country_from_rest(rest_country)

                self.name_repo.add_name_country(name_record.id, country.id, probability)
                result.append(NameCountryResponse(
                    name=name,
                    country=CountryDTO.from_orm(country),
                    probability=probability
                ))
            return result

        except APIError as e:
            handle_api_error(e)
        except DatabaseError as e:
            handle_database_error(e)
        except Exception as e:
            handle_api_error(APIError(f"Unexpected error while processing name {name}: {str(e)}"))

    async def get_popular_names_by_country(self, country_code: str) -> List[PopularNameResponse]:
        try:
            normalized_country_code = country_code.strip().upper()
            country = self.country_repo.get_country_by_code(normalized_country_code)
            if not country:
                raise APIError(f"Country code {normalized_country_code} not found")
            popular_names = self.name_repo.get_popular_names_by_country(normalized_country_code)
            if not popular_names:
                return []
            return [
                PopularNameResponse(
                    name=name.name,
                    count_of_requests=name.count_of_requests
                ) for name in popular_names
            ]
        except APIError as e:
            raise e
        except DatabaseError as e:
            raise e
        except Exception as e:
            raise APIError(f"Unexpected error while fetching popular names for country {country_code}: {str(e)}")
