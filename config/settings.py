
from pydantic import BaseModel
from decouple import config


class Settings(BaseModel):
    DEBUG: bool = config("DEBUG")
    PROJECT_TITLE: str = "Fastapi auth"

    USE_SQLITE_DB: str = config("USE_SQLITE_DB")

    POSTGRES_USER: str = config("POSTGRES_USER")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = config("POSTGRES_PORT")
    POSTGRES_DB: str = config("POSTGRES_DB")

    MAIL_USERNAME: str = config("MAIL_USERNAME")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD")
    MAIL_FROM: str = config("MAIL_FROM")
    TO_MAIL: str = config("TO_MAIL")
    MAIL_PORT: str = config("MAIL_PORT")
    MAIL_SERVER: str = config("MAIL_SERVER")

    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    SECRET_KEY: str = config("SECRET")
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: str = config("JWT_ALGORITHM")
    EMAIL_TOKEN_EXPIRY_MINUTES: int = 120

    ACCESS_TOKEN_EXPIRY_SECONDS: int = 900
    REFRESH_TOKEN_EXPIRY_DAYS: int = 30
    EMAIL_TOKEN_EXPIRY_MINUTES: int = 30
    RESET_TOKEN_EXPIRY_MINUTES: int = 30


    TIME_FORMAT: int = "%H:%M:%S"
    DATETIME_FORMAT: int = "%Y-%m-%d %H:%M:%S"
    DATE_TIME: int = "%Y-%m-%d:%H:%M"
    DATE_T: int = "%Y-%m-%dT%H:%M"
    DATE: int = "%Y-%m-%d"
    DATE_POINT: int = "%d.%m.%Y"
    DATE_L: int = "%Y-%m-%dT%H-%M"


settings = Settings()
