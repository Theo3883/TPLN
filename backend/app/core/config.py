from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://tpln:tpln_dev@localhost:5432/tpln"
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_api_key: str = "master_key_dev"
    meilisearch_index: str = "editions"
    rate_limit_reviews_per_hour: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
