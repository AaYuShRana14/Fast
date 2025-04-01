from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache
from typing import Optional
class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")

class GlobalConfig(BaseConfig):
    DATABASE_URL:Optional[str]=None
    DB_FORCE_ROLL_BACK:bool=False
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None

class DevConfig(GlobalConfig):
    model_config=SettingsConfigDict(env_prefix="DEV_")
class ProdConfig(GlobalConfig):
    model_config=SettingsConfigDict(env_prefix="PROD_")

class TestConfig(GlobalConfig):
    DATABASE_URL:str="sqlite:///data.db"
    DB_FORCE_ROLL_BACK:bool=True

@lru_cache
def get_config(env_state:str):
    config={"dev":DevConfig,"prod":ProdConfig,"test":TestConfig}
    return config.get(env_state, DevConfig)()

baseConfig=BaseConfig()
config=get_config(BaseConfig().ENV_STATE)

