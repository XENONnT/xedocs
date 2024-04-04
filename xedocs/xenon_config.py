
import os
import configparser

from typing import Any, Dict, Tuple

from pydantic import BaseSettings, BaseModel, SecretStr


def configparser_source(settings: BaseSettings) -> Dict[str, Any]:
    paths = []
    if "HOME" in os.environ:
        paths.append(os.path.join(os.environ["HOME"], ".xenon_config"))

    if "XENON_CONFIG" in os.environ:
        paths.append(os.environ["XENON_CONFIG"])

    paths = [os.path.expanduser(path) for path in paths]

    if not paths:
        return {}
    
    config = configparser.RawConfigParser()
    try:
        config.read(paths)
        return {section: dict(config.items(section)) 
                for section in config.sections() if section in settings.__fields__}
    except:
        return {}


class BasicConfig(BaseModel):
    logging_level = "warning"


class RunDBConfig(BaseModel):
    rundb_api_url: str = ""
    rundb_api_user: str = ""
    rundb_api_password: str = ""
    pymongo_url: str = ""
    pymongo_user: str = ""
    pymongo_password: str = ""
    pymongo_database: str = ""
    xent_url: str = ""
    xent_user: str = ""
    xent_password: str = ""
    xent_database: str = ""
    xe1t_url: str = ""
    xe1t_user: str = ""
    xe1t_password: str = ""
    xe1t_database: str = ""

    max_pool_size: int = 100
    socket_timeout: int = 60000
    connect_timeout: int = 60000
    read_preference: str = "secondaryPreferred"


class StraxenConfig(BaseModel):
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""


class ScadaConfig(BaseModel):
    sclogin_url: str = ""
    scdata_url: str = ""
    sclastvalue_url: str = ""
    straxen_username: str = ""
    straxen_password: str = ""
    pmt_parameter_names: str = ""


class XenonConfig(BaseSettings):
    basic: BasicConfig = BasicConfig()
    RunDB: RunDBConfig = RunDBConfig()
    straxen: StraxenConfig = StraxenConfig()
    scada: ScadaConfig = ScadaConfig()

    class Config:
        extra = "ignore"
        env_prefix = "XENON_CONFIG_"
        env_nested_delimiter = '__'
        case_sensitive = False

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            print(f"Parsing {field_name} from {raw_val}")
            return raw_val

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            
            sources = (
                init_settings,
                env_settings,
                configparser_source,
            )
            if os.path.isdir("/run/secrets"):
                sources = sources + (file_secret_settings,)
            return sources
