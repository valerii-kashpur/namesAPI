from typing import List

from fastapi import APIRouter, Depends, HTTPException

from src.api.routes.names import get_name_service
from src.api.schemas import PopularNameResponse
from src.exceptions.custom_exceptions import APIError, DatabaseError
from src.services.name_service import NameService

router = APIRouter(tags=["popular_names"])


@router.get("/popular-names/", response_model=List[PopularNameResponse])
async def get_popular_names_by_country(country: str, service: NameService = Depends(get_name_service)):
    if not country:
        raise HTTPException(status_code=400, detail="Country parameter is required")
    try:
        result = await service.get_popular_names_by_country(country)
        if not result:
            raise HTTPException(status_code=404, detail="No names found for this country")
        return result
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
