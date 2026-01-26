from http import HTTPStatus
from binascii import Error as BinasciiError
from json import JSONDecodeError
from logging import getLogger

from flask import Blueprint, request

from ..controllers.encryption import CryptingHandler
from ..helpers.crypters import Base64Crypter


blueprint_encryption = Blueprint("encryption", import_name="__name__")


@blueprint_encryption.route("/encrypt", methods=["POST"])
def encrypt():
    payload, encrypted = request.get_json(), {}

    handler = CryptingHandler(crypter=Base64Crypter())
    for key, value in payload.items():
        encrypted[key] = handler.encrypt(value)
    return encrypted, HTTPStatus.OK


@blueprint_encryption.route("/decrypt", methods=["POST"])
def decrypt():
    logger = getLogger(__name__)
    payload, decrypted = request.get_json(), {}

    handler = CryptingHandler(crypter=Base64Crypter())
    for key, value in payload.items():
        if not isinstance(value, str) or not handler.is_encrypted(value):
            decrypted[key] = value
            continue

        try:
            decrypted[key] = handler.decrypt(value)
        except (JSONDecodeError, UnicodeDecodeError, BinasciiError):
            logger.error("Unable to decrypt value for key: %s", key)
            return {"error": "One or more items were not properly encrypted"}, HTTPStatus.BAD_REQUEST
            
    return decrypted, HTTPStatus.OK
