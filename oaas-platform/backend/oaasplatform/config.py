import os, pathlib, logging, pytz
from functools import lru_cache

class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent

    DEBUG: bool = False
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'oaas_node')

    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    if LOG_LEVEL.upper() == "ERROR":
        LOG_LEVEL = logging.ERROR
    elif LOG_LEVEL.upper() == "DEBUG":
        LOG_LEVEL = logging.DEBUG
    else:
        LOG_LEVEL = logging.INFO

    TZ: str = os.environ.get('TZ', 'Europe/Madrid')
    TZ = pytz.timezone(TZ)

    POSTGRES_IP: str = os.environ.get('POSTGRES_IP', 'db')
    POSTGRES_PORT: int = os.environ.get('POSTGRES_PORT', '5432')
    POSTGRES_USER: str = os.environ.get('POSTGRES_USER', 'admin')
    POSTGRES_PASSWORD: str = os.environ.get('POSTGRES_PASSWORD', '123456789')
    POSTGRES_DB: str = os.environ.get('POSTGRES_DB', 'enp_auth')
    DATABASE_URL: str = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_IP}:{POSTGRES_PORT}/{POSTGRES_DB}"

    REGISTRY_URL: str = os.environ.get('REGISTRY_URL')
    REGISTRY_USER: str = os.environ.get('REGISTRY_USER')
    REGISTRY_PASSWORD: str = os.environ.get('REGISTRY_PASSWORD')

    # Force to be a boolean
    NETWORK_MODE_HOST: str = os.environ.get('NETWORK_MODE_HOST', "True")
    if NETWORK_MODE_HOST.upper() == "FALSE":
        NETWORK_MODE_HOST = False
    else:
        NETWORK_MODE_HOST = True
    
    OAAS_NODE_CONTAINER_NAME: str = "oaas-platform_backend"
    INTERNAL_PORT: int = 55955  # Internal Port of algorithm repo
    DISCOVERY_PORT: int = 5500
    INIT_PORT: int = 55000

    # OpenAPI definitions
    TITLE = "OaaS Platform Prototype API"
    VERSION = "1.0"
    DESCRIPTION = """ 
The Optimization as a Service (OaaS) platform prototype provides advanced network optimization solutions. Developed with Python and FastAPI, it uses an OpenAPI schema for standardized RESTful APIs. Key features include managing algorithm images, executing instances and allowing the execution of algorithms.

The platform's architecture supports dynamic resource orchestration, improving network performance and operational efficiency​​​​.
    
"""

    TAG_METADATA = [
        {
            "name": "Image Management module",
            "description": "Operations to manage resource images"
        },
        {
            "name": "Instance Management module",
            "description": "Operations to orchestrate instances"
        },
        {
            "name": "Execution Management module",
            "description": "Operations to launch and retrieve information of resources"
        },
        {
            "name": "Platform Management module",
            "description": "Operations to manage the platform"
        },
        {
            "name": "Designs handling module",
            "description": "Operations to manage the designs"
        },
        {
            "name": "Internal Callback",
            "description": "Operations for internal procedures"
        }
    ]

    pass

class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    SECURE = False
    pass

class ProductionConfig(BaseConfig):
    pass

@lru_cache
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }

    config_name = os.environ.get('FASTAPI_CONFIG', 'production')
    config_cls = config_cls_dict[config_name]

    return config_cls()

settings = get_settings()