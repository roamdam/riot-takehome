from archivist import LoggerBuilder
from flask import Flask, request
from http import HTTPStatus

from api.services.encryption import blueprint_encryption
from api.services.signature import blueprint_signature


logger = LoggerBuilder().build()
app = Flask(__name__)

app.register_blueprint(blueprint_encryption)
app.register_blueprint(blueprint_signature)
