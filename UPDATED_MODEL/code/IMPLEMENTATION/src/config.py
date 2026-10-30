"""
Configuration module for the Temporal-Valid Knowledge Graph RAG System.

This module handles loading environment variables and providing typed access
to configuration values. All sensitive values (API keys) are loaded from
environment and never logged.

Usage:
    from src.config import Settings, get_settings

    settings = get_settings()
    print(settings.model)  # Access configured model name
"""

from __future__ import annotations

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    All fields support .env file loading. Sensitive values (API keys, passwords)
    are loaded from environment but never logged or exposed in error messages.

    Attributes:
        openai_api_key: API key for OpenAI-compatible LLM gateway
        openai_base_url: URL of the internal LLM gateway endpoint
        model: Default LLM model to use for generation
        vlm_model: Vision-Language Model for document enrichment
        neo4j_uri: Bolt connection URI for Neo4j graph database
        neo4j_user: Neo4j authentication username
        neo4j_password: Neo4j authentication password
        qdrant_url: HTTP URL for Qdrant vector database
        watch_dir: Directory to watch for new documents (samples5/)
        audit_log_path: Path to append-only audit log file
    """

    # LLM Gateway Configuration (internal military gateway)
    openai_api_key: str = Field(
        default="",
        alias="OPENAI_API_KEY",
        description="API key for OpenAI-compatible LLM gateway",
    )
    openai_base_url: str = Field(
        default="http://llm-gateway.internal/v1",
        alias="OPENAI_BASE_URL",
        description="URL of the internal LLM gateway endpoint",
    )
    model: str = Field(
        default="gpt-4-turbo",
        alias="MODEL",
        description="Default LLM model for answer generation",
    )

    # Vision-Language Model Configuration
    vlm_model: str = Field(
        default="gpt-4o",
        alias="VLM_MODEL",
        description="VLM for document image/table/chart extraction",
    )

    # Graph Database Configuration (Neo4j for temporal KG)
    neo4j_uri: str = Field(
        default="bolt://localhost:7687",
        alias="NEO4J_URI",
        description="Neo4j bolt connection URI",
    )
    neo4j_user: str = Field(
        default="neo4j", alias="NEO4J_USER", description="Neo4j authentication username"
    )
    neo4j_password: str = Field(
        default="", alias="NEO4J_PASSWORD", description="Neo4j authentication password"
    )

    # Vector Database Configuration (Qdrant for embeddings)
    qdrant_url: str = Field(
        default="http://localhost:6333",
        alias="QDRANT_URL",
        description="Qdrant HTTP API URL",
    )

    # File Watch Configuration
    watch_dir: str = Field(
        default="./samples5",
        alias="WATCH_DIR",
        description="Directory to watch for new/modified documents",
    )

    # Audit Configuration
    audit_log_path: str = Field(
        default="./data/audit.jsonl",
        alias="AUDIT_LOG_PATH",
        description="Path to append-only audit log file",
    )

    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get cached application settings instance.

    Uses LRU cache to ensure single Settings instance across the application.
    Settings are loaded once from environment and .env file.

    Returns:
        Settings: The application configuration singleton

    Example:
        >>> settings = get_settings()
        >>> print(f"Using model: {settings.model}")
        Using model: gpt-4-turbo
    """
    return Settings()


# Provide module-level access for convenience
settings = get_settings()
