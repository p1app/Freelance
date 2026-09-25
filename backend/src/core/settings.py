from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )


class DatabaseConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="db_")

    host: str
    port: int
    name: str
    user: str
    password: str

    def get_db_url(self):
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.name}"
        )


class TestDatabaseConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="test_db_")

    host: str
    port: int
    name: str
    user: str
    password: str

    def get_db_url(self):
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.name}"
        )


class SecurityConfig(ConfigBase):
    algorithm: str
    secret_key: str
    access_token_expires: int
    refresh_token_expires: int

    model_config = SettingsConfigDict(env_prefix="sec_")


class EmailConfig(ConfigBase):
    login: str
    password: str

    model_config = SettingsConfigDict(env_prefix="email_")


class RedisConfig(ConfigBase):
    host: str
    port: int

    model_config = SettingsConfigDict(env_prefix="redis_")


class Config(BaseSettings):
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)  # type: ignore
    security: SecurityConfig = Field(default_factory=SecurityConfig)  # type: ignore
    email: EmailConfig = Field(default_factory=EmailConfig)  # type: ignore
    redis: RedisConfig = Field(default_factory=RedisConfig)  # type: ignore
    test_db: TestDatabaseConfig = Field(default_factory=TestDatabaseConfig)  # type: ignore


config = Config()
