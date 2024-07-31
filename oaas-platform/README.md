# OaaS Platform (prototype)

## Features
* A Docker Container Orchestator to deploy Algorithms Repositories and execute algorithms inside then.
* API based system that connect with OaaS Master (upper side) and Algorithms Repositories (lower side).

## Requires
* __Docker__, must be installed on host.
* PostgresSQL for SQL database. MySQL/MariaDB not allow.

## Database SQL migrations
### Initialize database models

* `docker compose exec oaas-platform aerich init -t oaasplatform.database.config.TORTOISE_ORM`
* `docker compose exec oaas-platform aerich init-db`

### Upgrade database models

* `docker compose exec oaas-platform aerich migrate`
* `docker compose exec oaas-platform aerich upgrade`

## Annotations
### First boot of app
An Error should be throw, this is default behaviour of app and is occured by the un-setup database. In order to setup the database, should execute the following command:

* `docker compose exec oaas-platform aerich init-db`

### `network_mode` on Windows
This apps extensly uses `network_mode` feature of Docker. This feature isnt able to be used on Windows. In order to use this app in a Windows environment you should replicate this steps:

1. Edit `docker-compose.yml`, go to `oaas-platform` section.
2. Remove/comment the line `network_mode: "host"`
3. Uncomment the section of ports, to enable the container to expose port `5000`.
4. Add a new `environment` with this value: `NETWORK_MODE_HOST=False`
5. Modify the `environment` *POSTGRES_IP* like this: `POSTGRES_IP=db`
6. Ensure that `container_name` is equals to: `oaas-platform_backend`

#### Distmatch behaviour
Detected distmatch with `network_mode` set as `host`:

* When using `NETWORK_MODE_HOST=False`, executing some calls on Swagger/OpenAPI throws and error on view (TypeError: NetworkError when attempting to fetch resource). Although, the endpoint could reach the sucesfull status, but they dont return data to Swagger/OpenAPI. Should check the console log to verify if the operations completes sucesful. Some endpoints with this behaviour:
    - *POST*  -  /algorithmRepositories
    - *POST*  -  /algorithmExecutions/{executionId}

