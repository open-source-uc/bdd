from pathlib import Path
from pydantic import BaseSettings

class Config(BaseSettings):
    db_name: str = "database"
    db_user: str = "user"
    db_password: str = "password"
    db_host: str = "localhost"
    api_base_path: Path = Path("/api")

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

config = Config()

