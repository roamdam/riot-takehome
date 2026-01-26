from archivist import LoggerBuilder
from flask import Flask
from flasgger import Swagger

from api.services.encryption import blueprint_encryption
from api.services.signature import blueprint_signature


logger = LoggerBuilder().build()
app = Flask(__name__)

app.register_blueprint(blueprint_encryption)
app.register_blueprint(blueprint_signature)

swagger = Swagger(app)


if __name__ == "__main__":
    app.run(debug=True)
