from binascii import Error as BinasciiError
from http import HTTPStatus
from json import JSONDecodeError
from logging import getLogger

from flask import Blueprint, request

from ..controllers.encryption import CryptingHandler
from ..helpers.crypters import Base64Crypter


blueprint_encryption = Blueprint("encryption", import_name="__name__")


@blueprint_encryption.route("/encrypt", methods=["POST"])
def encrypt():
    """
    Encrypt all depth-1 values in the received JSON payload.

    ---
    post:
        summary: Encrypt depth-1 values of a JSON object
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        additionalProperties: true
                    example:
                        name: Alice
                        age: 32
                        active: true
                        metadata:
                            country: FR
        responses:
            200:
                description: Successfully encrypted JSON object
                content:
                    application/json:
                        schema:
                            type: object
                            additionalProperties: true
                        example:
                            active: '@@enc@@v1::dHJ1ZQ=='
                            age: '@@enc@@v1::MzI='
                            metadata: '@@enc@@v1::eyJjb3VudHJ5IjogIkZSIn0='
                            name: '@@enc@@v1::IkFsaWNlIg=='
            400:
                description: Invalid input payload (payload is not a JSON object)
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                error:
                                    type: string
        tags:
            - encryption
    """
    payload, encrypted = request.get_json(), {}

    handler = CryptingHandler(crypter=Base64Crypter())
    for key, value in payload.items():
        encrypted[key] = handler.encrypt(value)
    return encrypted, HTTPStatus.OK


@blueprint_encryption.route("/decrypt", methods=["POST"])
def decrypt():
    """
    Decrypt depth-1 items from payload. If an item was not encrypted, it is returned as is.

    ---
    post:
        summary: Decrypt the depth-1 values of a JSON object
        description: >
            Decrypts all depth-1 values of the provided JSON object that were previously
            encrypted by us. Values that are not encrypted by us are returned unchanged. If any
            decryption fails, a BadRequest error is returned.
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        additionalProperties: true
                    example:
                        active: '@@enc@@v1::dHJ1ZQ=='
                        age: '@@enc@@v1::MzI='
                        metadata: '@@enc@@v1::eyJjb3VudHJ5IjogIkZSIn0='
                        name: '@@enc@@v1::IkFsaWNlIg=='
                        comment: Clear value
        responses:
            200:
                description: Successfully decrypted JSON object
                content:
                    application/json:
                        schema:
                            type: object
                            additionalProperties: true
                        example:
                            name: Alice
                            age: 32
                            active: true
                            metadata:
                                country: FR
                            comment: Clear value
            400:
                description: Invalid input payload or malformed encrypted value
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                error:
                                    type: string
        tags:
            - encryption
    """
    logger = getLogger(__name__)
    payload, decrypted = request.get_json(), {}

    handler = CryptingHandler(crypter=Base64Crypter())
    for key, value in payload.items():
        if not isinstance(value, str) or not handler.is_encrypted(value):
            decrypted[key] = value
            continue

        try:
            decrypted[key] = handler.decrypt(value)
        except (JSONDecodeError, UnicodeDecodeError, BinasciiError, UnicodeEncodeError):
            logger.error("Unable to decrypt value for key: %s", key)
            return {"error": "One or more items were not properly encrypted"}, HTTPStatus.BAD_REQUEST

    return decrypted, HTTPStatus.OK
