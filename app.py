from archivist import LoggerBuilder
from flask import Flask, jsonify

from api.config.apispec import spec
from api.config.definitions import API_URL, SWAGGER_URL, ROOT_URL
from api.services.encryption import blueprint_encryption
from api.services.signature import blueprint_signature
from api.services.swagger import swagger_ui_blueprint


logger = LoggerBuilder().build(template="rotating")
logger.debug("Start API Service")

app = Flask(__name__)
app.register_blueprint(blueprint_encryption, url_prefix=ROOT_URL)
app.register_blueprint(blueprint_signature, url_prefix=ROOT_URL)


with app.test_request_context():
    for fn_name, fn_view in app.view_functions.items():
        if fn_name == "static":
            continue
        logger.debug(f"Loading swagger docs for {fn_name}")
        spec.path(view=fn_view)
        logger.debug(f"Loaded swagger docs for {fn_name}")


@app.route(API_URL)
def swagger():
    """Swagger API definition."""
    return jsonify(spec.to_dict())


app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == "__main__":
    app.run()
