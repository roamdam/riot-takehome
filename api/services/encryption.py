from http import HTTPStatus, HTTPMethod
from logging import getLogger

from flask import Blueprint, request

from ..controllers.encryption import EncryptionHandler
from ..helpers.crypters import Base64Crypter


blueprint_encryption = Blueprint("encryption", import_name="__name__")


@blueprint_encryption.route("/encrypt", methods=[HTTPMethod.POST])
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
                            active: --- BEGIN CRYPTED MESSAGE ---dHJ1ZQ==
                            age: --- BEGIN CRYPTED MESSAGE ---MzI=
                            metadata: --- BEGIN CRYPTED MESSAGE ---eyJjb3VudHJ5IjogIkZSIn0=
                            name: --- BEGIN CRYPTED MESSAGE ---IkFsaWNlIg==
            400:
                description: Invalid input payload (payload is not a JSON object)
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                error:
                                    type: string
            500:
                description: Unable to encrypt message
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
    payload = request.get_json()
    if not isinstance(payload, dict):
        return {"error": "Input is not a valid JSON"}, HTTPStatus.BAD_REQUEST

    handler = EncryptionHandler(crypter=Base64Crypter())
    try:
        result, status = handler.encrypt_payload(payload)
    except Exception as e:
        logger.error("Error when encrypting payload", exc_info=e)
        result, status = {"error": "Unable to encrypt payload"}, HTTPStatus.INTERNAL_SERVER_ERROR
    return result, status


@blueprint_encryption.route("/decrypt", methods=[HTTPMethod.POST])
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
                        active: --- BEGIN CRYPTED MESSAGE ---dHJ1ZQ==
                        age: --- BEGIN CRYPTED MESSAGE ---MzI=
                        metadata: --- BEGIN CRYPTED MESSAGE ---eyJjb3VudHJ5IjogIkZSIn0=
                        name: --- BEGIN CRYPTED MESSAGE ---IkFsaWNlIg==
                        comment: Not encrypted
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
                            comment: Not encrypted
            400:
                description: Invalid input payload or malformed encrypted value
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                error:
                                    type: string
            500:
                description: Unable to decrypt message
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
    payload = request.get_json()
    if not isinstance(payload, dict):
        return {"error": "Input is not a valid JSON"}, HTTPStatus.BAD_REQUEST

    handler = EncryptionHandler(crypter=Base64Crypter())
    try:
        result, status = handler.decrypt_payload(payload)
    except Exception as e:
        logger.error("Error when encrypting payload", exc_info=e)
        result, status = {"error": "Unable to decrypt payload"}, HTTPStatus.INTERNAL_SERVER_ERROR
    return result, status
