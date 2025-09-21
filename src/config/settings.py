"""Configuration settings for the email agent."""

import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Email Configuration
    email_provider: str = Field("gmail", env="EMAIL_PROVIDER")
    email_address: str = Field(..., env="EMAIL_ADDRESS")
    email_password: str = Field(..., env="EMAIL_PASSWORD")
    imap_server: str = Field("imap.gmail.com", env="IMAP_SERVER")
    imap_port: int = Field(993, env="IMAP_PORT")
    
    # Agent Configuration
    agent_name: str = Field("EmailAssistant", env="AGENT_NAME")
    agent_mode: str = Field("development", env="AGENT_MODE")
    max_emails_per_batch: int = Field(50, env="MAX_EMAILS_PER_BATCH")
    auto_execute_actions: bool = Field(False, env="AUTO_EXECUTE_ACTIONS")
    
    # Database
    database_url: str = Field("sqlite:///email_agent.db", env="DATABASE_URL")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()