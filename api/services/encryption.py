from http import HTTPStatus

from flask import Blueprint, request

from ..helpers.encryption import Encrypter


blueprint_encryption = Blueprint("encryption", import_name="__name__")


@blueprint_encryption.route("/encrypt", methods=["POST"])
def encrypt():
    payload, encrypted = request.get_json(), {}
    crypter = Encrypter()
    for key, value in payload.items():
        encrypted[key] = crypter.encrypt(value)
    return encrypted, HTTPStatus.OK


@blueprint_encryption.route("/decrypt", methods=["POST"])
def decrypt():
    payload, decrypted = request.get_json(), {}
    crypter = Encrypter()
    for key, value in payload.items():
        if not isinstance(value, str) or not crypter.is_encrypted(value):
            decrypted[key] = value
        else:
            decrypted[key] = crypter.decrypt(value)
    return decrypted, HTTPStatus.OK
