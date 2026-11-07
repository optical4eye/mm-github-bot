from pydantic import BaseModel, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class RepoConfig(BaseModel):
    owner: str = Field(..., min_length=1)
    repo: str = Field(..., min_length=1)


class MattermostConfig(BaseModel):
    webhook_url: HttpUrl


class Config(BaseModel):
    repositories: List[RepoConfig] = Field(..., min_length=1)
    check_interval_seconds: int = Field(default=3600, ge=60)
    mattermost: Optional[MattermostConfig] = None
    state_file: str = "/data/state.json"
    log_level: str = "INFO"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    config_path: str = "/app/config.yaml"
    mm_webhook_url: Optional[str] = None