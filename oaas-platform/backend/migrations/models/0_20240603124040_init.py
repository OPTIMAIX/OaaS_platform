from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "images" (
    "imageId" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(40) NOT NULL UNIQUE,
    "description" VARCHAR(260) NOT NULL,
    "imageUrl" VARCHAR(50) NOT NULL,
    "type" VARCHAR(20) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "images"."type" IS 'PYTHON: python\nFASTAPI_REDIS: fastapi-redis\nJAVA: java\nMATLAB: matlab';
CREATE TABLE IF NOT EXISTS "instances" (
    "instanceId" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(40) NOT NULL UNIQUE,
    "description" VARCHAR(260) NOT NULL,
    "status" VARCHAR(20),
    "quotaInformation" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "docker" JSONB,
    "image_id" INT NOT NULL REFERENCES "images" ("imageId") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "resourcedescriptors" (
    "resourceId" SERIAL NOT NULL PRIMARY KEY,
    "localId" INT NOT NULL,
    "name" VARCHAR(40) NOT NULL,
    "version" VARCHAR(10) NOT NULL,
    "description" VARCHAR(260) NOT NULL,
    "execution_type" VARCHAR(20) NOT NULL  DEFAULT 'OaaS',
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "inputParametersTemplate" JSONB,
    "outputParametersTemplateSuccess" JSONB,
    "outputParametersTemplateFailure" JSONB,
    "images_id" INT NOT NULL REFERENCES "images" ("imageId") ON DELETE CASCADE
);
COMMENT ON COLUMN "resourcedescriptors"."execution_type" IS 'OAAS: OaaS\nDIRECT: direct';
CREATE TABLE IF NOT EXISTS "executions" (
    "executionId" SERIAL NOT NULL PRIMARY KEY,
    "status" INT,
    "lastProgress" VARCHAR(30),
    "lastProgressFraction" DOUBLE PRECISION,
    "executionRequest" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "executionStart" TIMESTAMPTZ,
    "executionEnd" TIMESTAMPTZ,
    "input_parameters" JSONB,
    "output_success" JSONB,
    "output_error" VARCHAR(100),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "instance_id" INT NOT NULL REFERENCES "instances" ("instanceId") ON DELETE CASCADE,
    "resource_id" INT NOT NULL REFERENCES "resourcedescriptors" ("resourceId") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
