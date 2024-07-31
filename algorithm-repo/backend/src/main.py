from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        debug=False,
        title="Algorithm Repo Debug",
        description="Init version algorithm repo",
        version="0.1.0"
    )

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Enable Logging
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info("Starting up...")

    # Creating algorithms file
    from src.utils.algorithms_wrapper import create_algorithms_file
    logger.info("Creating algorithms.json...")
    create_algorithms_file()

    # Creating executions file
    from src.utils.executions_wrapper import create_executions_file
    logger.info("Creating executions.json...")
    create_executions_file()

    # Set-up Routes
    from src.routes import algorithms, executions
    app.include_router(algorithms.router)
    app.include_router(executions.router)

    # default route
    @app.get("/", include_in_schema=False)
    def home():
        return f"Welcome to XXXX! Go to '/docs' or '/redoc' to view the API definition."

    # default callback
    @app.post("/callback/{id}", include_in_schema=False)
    def callback(id: int, content: dict):
        logger.info(f"Callback {id}. Content: {content}")
        return content

    return app

app = create_app()
