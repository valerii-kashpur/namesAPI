from datetime import datetime, timedelta

import jwt


def create_jwt_token(
    data: dict, secret_key: str, algorithm: str, expires_minutes: int
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)
