# OaaS Platform (prototype)

## Overview

The **Optimization as a Service (OaaS)** platform is designed to orchestrate and execute optimization algorithms within a network context, leveraging containerized environments for flexible deployment. This prototype includes APIs to manage resources, orchestrate executions, and communicate with other platform components.

## Disclaimer

This project is a **prototype** version of the Optimization as a Service (OaaS) platform. It is primarily intended for testing and evaluation purposes. As a prototype, certain features may be incomplete or behave differently than expected in production-ready software.

Users should be aware that the platform may experience the following:

- **Instability**: There may be unexpected crashes or failures under specific conditions.
- **Limited Functionality**: Not all intended features have been fully implemented or optimized.
- **Performance Variations**: Performance metrics such as speed and resource usage may not reflect the final, optimized version of the platform.

## Folder Structure

```bash
oaas-platform/
│
├── backend/                 # Core platform codebase
│   ├── Dockerfile           # Docker configuration for the backend
│   ├── migrations/          # Database migration files
│   ├── oaasplatform/        # Main backend service
│   │   ├── config.py        # Configuration settings
│   │   ├── crud/            # CRUD operations for database interactions
│   │   ├── database/        # Database initialization and connection logic
│   │   ├── main.py          # Main entry point for the FastAPI app
│   │   ├── routes/          # API route definitions
│   │   ├── schemas/         # Pydantic models and schemas
│   │   └── utils/           # Utility functions and helper scripts
│   ├── poetry.lock          # Dependency lock file
│   ├── pyproject.toml       # Python project configuration
│   └── tests/               # Unit and integration tests
├── docker-compose.yml       # Docker Compose setup for the entire platform
├── playbooks/               # Ansible playbooks for platform validations
└── README.md                # This documentation file
```

## Features

* __Docker Container Orchestration__: Deploy and manage algorithm repositories, allowing for algorithm executions in isolated container environments.

* __API-Based Architecture__: FastAPI-based system enabling interaction with OaaS Master (upper layer) and Algorithm Repositories (lower layer).

## Requirements

* __Docker__: Ensure that Docker is installed on the host machine.
* __PostgreSQL__: A PostgreSQL instance is required for database operations. Note: MySQL/MariaDB is not supported.

## Database Setup and Migrations
### Initialize database 
To initialize the database models, run the following commands:
```bash
docker compose exec oaas-platform aerich init -t oaasplatform.database.config.TORTOISE_ORM
docker compose exec oaas-platform aerich init-db
```

### Upgrade database models
To apply database migrations, use:

```bash
docker compose exec oaas-platform aerich migrate
docker compose exec oaas-platform aerich upgrade
```

## Deployment instructions
### First boot
Upon the first boot, the application may throw an error due to the uninitialized database. This is expected. Run the following command to initialize the database:

```bash
docker compose exec oaas-platform aerich init-db
```
### Regular Boot

To start the OaaS platform normally after initial setup, you can use Docker Compose to build and run the services in the project. This process ensures that all necessary services (backend, database, etc.) are started and interconnected as defined in the `docker-compose.yml` file.

#### Steps for Regular Boot

1. **Ensure Prerequisites Are Met**:
   - Docker must be installed and running on your host machine.
   - You should have already initialized the database if this is the first time you are running the platform (see [Database Setup and Migrations](#database-setup-and-migrations)).

2. **Build the Docker Images**:
   If you haven't built the images before or you have made changes to the codebase, you need to build the containers:
   
   ```
   docker compose up --build
    ```

This command does the following:

 - Builds the Docker images for the platform, ensuring that the latest changes are incorporated.
- Starts up the backend service and all necessary containers (e.g., PostgreSQL) in the correct sequence as defined in docker-compose.yml.

3. __Monitoring the Logs__: As Docker Compose starts the containers, you will see logs output to the console. These logs allow you to monitor the startup process and verify that the services are running correctly.

4. __Accessing the API__: Once the containers are up and running, you can access the FastAPI backend, including the API documentation via Swagger, by visiting:

    ```bash
    http://localhost:5000/docs
    ```

5. __Stopping the Platform__: To stop all services gracefully, use:

    ```bash
    docker compose down
    ```

    This command stops and removes all containers associated with the OaaS platform, cleaning up resources.

##### Additional Notes:

* __Rebuilding Images__: If you've made changes to the Dockerfile or other dependencies, always use the `--build` flag to ensure the images are rebuilt.

* __Detached Mode__: If you want to run the containers in the background, add the -d option:

    ```bash
    docker compose up --build -d
    ```
This will start all services in detached mode, freeing up your terminal for other tasks.

### Windows Specific Instructions
Due to Docker's extensive use of network_mode: host, additional steps are required for Windows environments:

1. Edit `docker-compose.yml` and modify the oaas-platform service:

    * Comment out `network_mode: "host"`.
    * Uncomment the ports section to expose port `5000`.

2. Add an environment variable `NETWORK_MODE_HOST=False`.
3. Modify the `POSTGRES_IP` environment variable to `POSTGRES_IP=db`.
4. Ensure the `container_name` is set to `oaas-platform_backend`.

#### Known Issues on Windows
When using Swagger/OpenAPI UI, some API endpoints may encounter NetworkError when using `NETWORK_MODE_HOST=False`, although the backend will still complete the operations. These include:

* __POST__ - /images
* __POST__ - /executions/{executionId}

In such cases, verify the operation in the console logs.
