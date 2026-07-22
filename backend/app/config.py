"""
Central application configuration.
All values are loaded from environment variables (see .env.example).
Nothing here is a placeholder — every setting is actually consumed by the
service that needs it (MySQL, Neo4j, ChromaDB, Firebase, Gemini).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    APP_NAME: str = "FactoryBrain AI"
    ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # --- MySQL ---
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "factorybrain"
    MYSQL_PASSWORD: str = "factorybrain_pw"
    MYSQL_DATABASE: str = "factorybrain"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    # --- Neo4j (Aura or self-hosted) ---
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "factorybrain_pw"

    # --- ChromaDB ---
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION: str = "factorybrain_documents"

    # --- Firebase ---
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CREDENTIALS_PATH: str = "/app/secrets/firebase-service-account.json"
    FIREBASE_WEB_API_KEY: str = ""

    # --- Gemini ---
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # --- OCR ---
    TESSERACT_CMD: str = "/usr/bin/tesseract"

    # --- Storage ---
    UPLOAD_DIR: str = "/app/storage/uploads"

    # --- RAG ---
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 6

    # --- Celery / Redis (background job queue for document processing) ---
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
