from flask import Blueprint, request
from http import HTTPMethod, HTTPStatus
from logging import getLogger

from ..config.fields import SignatureFields
from ..controllers.signature import SignatureHandler
from ..helpers.signer import HMACSigner


blueprint_signature = Blueprint("signature", import_name="__name__")


@blueprint_signature.route("/sign", methods=[HTTPMethod.POST])
def sign():
    """
    Generate signature for received JSON payload.

    ---
    post:
        summary: Generate signature for a JSON object
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
        responses:
            200:
                description: Successfully generated signature
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                signature:
                                    type: string
                        example:
                            signature: a1b2c3d4e5f6g7h8i9j0
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
                description: Unable to sign message
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                error:
                                    type: string
        tags:
            - signature
    """
    # We accept non-dict JSON input, such as a single string, null, a list...
    #   but still raises a BAD REQUEST if get_json did not return properly
    payload = request.get_json(silent=True)
    if payload is None:
        return {"error": "Invalid JSON payload"}, HTTPStatus.BAD_REQUEST
    logger = getLogger(__name__)

    handler = SignatureHandler(signer=HMACSigner())
    try:
        result, status = handler.sign_payload(payload)
    except Exception as e:
        logger.error("Error when signing payload", exc_info=e)
        result, status = {"error": "Unable to sign payload"}, HTTPStatus.INTERNAL_SERVER_ERROR
    return result, status


@blueprint_signature.route("/verify", methods=[HTTPMethod.POST])
def verify():
    """
    Verify data within payload against provided signature.

    ---
    post:
        summary: Verify signature for a JSON object
        description: >
            Verify that the `data` object provided matches with the signature provided.
            Verification is not dependant on the order of keys within the data object.
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            signature:
                                type: string
                            data:
                                type: object
                                additionalProperties: true
                        required:
                            - signature
                            - data
                    example:
                        signature: 8e11628db50eae6b5bf482d2afb3eaac46eb832ff28b45b2f2b30c1cdcecafaa
                        data:
                            name: Alice
                            age: 32
        responses:
            204:
                description: Verification successful
            400:
                description: Invalid signature or invalid data
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
            - signature
    """
    logger = getLogger(__name__)
    payload = request.get_json()

    # Validate that signature and data are present in payload. With more time we'd use a schema validation decorator
    if not isinstance(payload, dict) or SignatureFields.signature not in payload or SignatureFields.data not in payload:
        return {"error": "Missing signature or data in payload"}, HTTPStatus.BAD_REQUEST

    handler = SignatureHandler(signer=HMACSigner())
    try:
        result, status = handler.verify_payload(payload)
    except Exception as e:
        logger.error("Error when verifying payload", exc_info=e)
        result, status = {"error": "Unable to verify payload"}, HTTPStatus.INTERNAL_SERVER_ERROR
    return result, status
