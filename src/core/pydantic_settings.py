from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
        )

class DatabaseConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="db_")

    host: str
    port: int
    name: SecretStr
    user: SecretStr
    password: SecretStr
