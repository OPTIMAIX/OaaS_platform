from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from tortoise import Tortoise

import logging, os

from oaasplatform.config import settings
from oaasplatform.utils import docker_register
from oaasplatform.database.register import register_tortoise
from oaasplatform.database.config import TORTOISE_ORM

logger  = logging.getLogger(__name__)

def create_app() -> FastAPI:
    # enable schemas
    Tortoise.init_models(["oaasplatform.database.models"], "models")

    # Enable Logging
    logger.setLevel(settings.LOG_LEVEL)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info("Starting up...")
    logger.debug(f"Environment: {os.environ.get('FASTAPI_CONFIG')}")
    logger.debug(f"Database: {settings.DATABASE_URL}")

    # Self-Test Docker
    from oaasplatform.utils.docker import selftest_docker
    if not selftest_docker():
        logger.error("Unable to connecto to Docker. Re-check the installation.")
    else:
        logger.info("Docker succesfully connected!")

    logger.info(f"Using system with network_mode_host: {settings.NETWORK_MODE_HOST}")

    app = FastAPI(
        debug=settings.DEBUG,
        openapi_tags=settings.TAG_METADATA,
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
    )

    if settings.NETWORK_MODE_HOST:
        # Enable CORS
        logger.info("Enabling CORS!")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
    # Setting up database & models
    register_tortoise(app, config=TORTOISE_ORM, generate_schemas=False)

    # Add registers for docker
    docker_register.register_start_instances(app=app)
    docker_register.register_stop_instances(app=app)

    from oaasplatform.routes import images, instances, executions, callback, management, designs

    app.include_router(images.router)
    app.include_router(instances.router)
    app.include_router(executions.router)
    app.include_router(management.router)
    app.include_router(designs.router)
    app.include_router(callback.router)

    if settings.DEBUG:
        from oaasplatform.routes import debug
        app.include_router(debug.router)

    # Enable FastAPI-Pagination
    add_pagination(app)

    # Get info of running system
    from oaasplatform.nocrud.info import get_info_startup
    get_info_startup()

    # Register to OaaS Master
    from oaasplatform.utils.master import register_to_master
    if register_to_master():
        logger.info("Succesfully registered to OaaS Master!")    
    else:
        logger.error("OaaS Master not respond")

    # default route
    @app.get("/", include_in_schema=False)
    def home():
        return f"Welcome to OaaS Platform API! Go to '/docs' or '/redoc' to view the API definition."

    return app

app = create_app()