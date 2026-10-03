# Назовем этот файл, например, src/core/config.py
import sys

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

IS_TESTING = "pytest" in sys.modules or "pytest" in sys.argv


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )


class DatabaseConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="DB_")
    HOST: str
    PORT: int
    NAME: str
    USER: str
    PASSWORD: str
    TEST_NAME: str = Field(default="freelance_test")

    def get_db_url(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    def get_test_url(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.TEST_NAME}"


class SecurityConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="SEC_")
    ALGORITHM: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRES: int
    REFRESH_TOKEN_EXPIRES: int


class EmailConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="EMAIL_")
    LOGIN: str = Field(default="")
    PASSWORD: str = Field(default="")


class RedisConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="REDIS_")
    HOST: str
    PORT: int


class Config(BaseSettings):
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)


config = Config()
