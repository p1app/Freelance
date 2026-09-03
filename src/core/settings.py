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
    name: str
    user: str
    password: str
    
    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.user}:{self.password}@"
                f"{self.host}:{self.port}/{self.name}")

class Config(BaseSettings):
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)


config = Config()

print(config.db.get_db_url())