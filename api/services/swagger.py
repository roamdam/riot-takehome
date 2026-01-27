from flask_swagger_ui import get_swaggerui_blueprint

from ..config.definitions import SWAGGER_URL, API_URL


swagger_ui_blueprint = get_swaggerui_blueprint(
    base_url=SWAGGER_URL,
    api_url=API_URL,
    config={"app_name": "Riot Takehome API Documentation"}
)
