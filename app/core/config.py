from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY", validation_alias="OPENAI_API_KEY")
    faiss_index_path: str = "faiss_index.bin"
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 500
    chunk_overlap: int = 100
    
    # Auth and Database Settings
    database_url: str = Field(default="sqlite+aiosqlite:///./interview_engine.db", alias="DATABASE_URL")
    jwt_secret: str = Field(default="YOUR_SUPER_SECRET_KEY_CHANGE_IN_PRODUCTION", alias="JWT_SECRET")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def get_database_url(self) -> str:
        """
        Railway and many PaaS providers inject DATABASE_URL starting with postgres:// or postgresql://.
        SQLAlchemy's asyncpg engine requires postgresql+asyncpg://.
        This property handles the conversion automatically while keeping local SQLite working seamlessly.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

settings = Settings()
