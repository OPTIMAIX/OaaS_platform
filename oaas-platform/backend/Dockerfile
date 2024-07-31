FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Madrid

# Install Poetry
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get remove -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Disable Poetry's virtual environment creation as Docker is already an isolated environment
RUN poetry config virtualenvs.create false

# Copy the project configuration files into the Docker image
COPY pyproject.toml poetry.lock* /app/

# Install project dependencies using Poetry
RUN poetry install --no-dev --no-interaction --no-ansi

# for migrations
# check if folder exists
ARG folder_path=migrations
RUN if [ -d "$folder_path" ]; then \
      # copy folder if it exists
      COPY $folder_path migrations/.; \
    fi

COPY oaasplatform/ /app/oaasplatform/

EXPOSE 5000

# Set the default command to run your application
# The environment variable FASTAPI_CONFIG is used to determine if migrations should be applied and if the server should reload
ENV FASTAPI_CONFIG=$FASTAPI_CONFIG  
CMD if [ "$FASTAPI_CONFIG" = "development" ] ; then \
    aerich upgrade; uvicorn oaasplatform.main:app --reload --host 0.0.0.0 --port 5000; \
  else \
     aerich upgrade; uvicorn oaasplatform.main:app --host 0.0.0.0 --port 5000; \
  fi