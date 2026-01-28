from os import environ


# Swagger and API spec
ROOT_URL = "/api"
SWAGGER_URL = f"{ROOT_URL}/docs"
API_URL = f"{ROOT_URL}/swagger.json"

# Load project environment variables
HMAC_SECRET = environ.get("HMAC_SECRET", "")
