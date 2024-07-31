from oaasplatform.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "oaasplatform.database.models", "aerich.models"
            ],
            "default_connection": "default"
        }
    },
    "use_tz": True,
    "timezone": "Europe/Madrid"
}