from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, SecurityScopes
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.services.auth_service import auth_get_current_user

bearer_scheme = HTTPBearer()


def get_current_user(
        security_scopes: SecurityScopes = SecurityScopes(),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db)
):
    return auth_get_current_user(security_scopes, credentials, db)
