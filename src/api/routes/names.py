from typing import List

from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas import NameCountryResponse
from src.clients.nationalize import NationalizeClient
from src.clients.rest_countries import RestCountriesClient
from src.database.db import get_db
from src.repositories.country_repository import CountryRepository
from src.repositories.name_repository import NameRepository
from src.services.name_service import NameService

router = APIRouter(tags=["names"])


def get_name_service(db=Depends(get_db)):
    nationalize_client = NationalizeClient()
    rest_countries_client = RestCountriesClient()
    name_repo = NameRepository(db)
    country_repo = CountryRepository(db)
    return NameService(nationalize_client, rest_countries_client, name_repo, country_repo)


@router.get("/names/", response_model=List[NameCountryResponse])
async def get_countries_by_name(name: str, service: NameService = Depends(get_name_service)):
    if not name:
        raise HTTPException(status_code=400, detail="Name parameter is required")
    result = await service.get_countries_by_name(name)
    if not result:
        raise HTTPException(status_code=404, detail="No countries found for this name")
    return result
