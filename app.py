from archivist import LoggerBuilder
from flask import Flask, request
from http import HTTPStatus


logger = LoggerBuilder().build()
app = Flask(__name__)


@app.route("/encrypt", methods=["POST"])
def encrypt():
    """Encrypt the input json."""
    body = request.get_json()
    body["updated"] = "Cool !"
    return body, HTTPStatus.OK
