from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security

from src.api.schemas import NameCountryResponse
from src.dependencies.names_deps import get_name_service
from src.dependencies.user_deps import get_current_user
from src.services.name_service import NameService

router = APIRouter(tags=["names"])


@router.get("/names/", response_model=List[NameCountryResponse])
async def get_countries_by_name(
    name: str,
    service: NameService = Depends(get_name_service),
    current_user=Security(get_current_user),
):
    if not name:
        raise HTTPException(status_code=400, detail="Name parameter is required")
    result = await service.get_countries_by_name(name)
    if not result:
        raise HTTPException(status_code=404, detail="No countries found for this name")
    return result
