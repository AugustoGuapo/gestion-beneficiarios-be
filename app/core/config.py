from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:"
            f"{self.db_password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"

settings = Settings()