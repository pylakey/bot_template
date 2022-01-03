from pydantic import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    BOT_API_ID: int
    BOT_API_HASH: str
    BOT_TOKEN: str
    POSTGRES_PASSWORD: str

    # Files settings
    DATA_DIR: str = ".data"
    SESSIONS_DIR: str = ".data/sessions"

    # noinspection PyPep8Naming
    @property
    def BOT_ID(self) -> int:
        return int(self.BOT_TOKEN.split(":")[0])


settings = Settings()
