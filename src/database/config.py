from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/names_db"
    POSTGRES_USER: str = "user"  # Добавляем поле
    POSTGRES_PASSWORD: str = "password"  # Добавляем поле
    POSTGRES_DB: str = "names_db"  # Добавляем поле
    POSTGRES_URL: str = "postgresql://user:password@localhost:5432/names_db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


db_settings = DatabaseSettings()
