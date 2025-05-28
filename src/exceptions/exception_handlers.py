from fastapi import HTTPException

from src.exceptions.custom_exceptions import APIError, DatabaseError


def handle_api_error(e: Exception) -> None:
    if isinstance(e, APIError):
        raise HTTPException(status_code=e.status_code, detail=e.message)
    raise HTTPException(status_code=500, detail=str(e))


def handle_database_error(e: Exception) -> None:
    if isinstance(e, DatabaseError):
        raise HTTPException(status_code=500, detail=e.message)
    raise HTTPException(status_code=500, detail=str(e))
