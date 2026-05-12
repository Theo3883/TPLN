from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://tpln:tpln@127.0.0.1:5433/tpln"
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_api_key: str = "master_key_dev"
    meilisearch_index: str = "editions"
    rate_limit_reviews_per_hour: int = 10
    db_ssl: bool = False  # set True in production
    
    # JWT Authentication
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
