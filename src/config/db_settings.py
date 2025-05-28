from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/names_db"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "names_db"
    POSTGRES_URL: str = "postgresql://user:password@localhost:5432/names_db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


db_settings = DatabaseSettings()
