from fastapi import Depends
from sqlalchemy.orm import Session

from src.clients.nationalize import NationalizeClient
from src.clients.rest_countries import RestCountriesClient
from src.database.db import get_db
from src.repositories.country_repository import CountryRepository
from src.repositories.name_repository import NameRepository
from src.services.name_service import NameService


def get_name_service(db: Session = Depends(get_db)):
    nationalize_client = NationalizeClient()
    rest_countries_client = RestCountriesClient()
    name_repo = NameRepository(db)
    country_repo = CountryRepository(db)
    return NameService(
        nationalize_client, rest_countries_client, name_repo, country_repo
    )
