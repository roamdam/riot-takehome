from flask import Blueprint, request
from http import HTTPStatus

from ..config.fields import SignatureFields
from ..controllers.signature import SignatureHandler
from ..helpers.signer import HMACSigner


blueprint_signature = Blueprint("signature", import_name="__name__")


@blueprint_signature.route("/sign", methods=["POST"])
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
                            signature: 'a1b2c3d4e5f6g7h8i9j0'
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
            - signature
    """
    payload, output = request.get_json(), {}
    handler = SignatureHandler(signer=HMACSigner())

    output[SignatureFields.signature] = handler.sign(payload)
    return output, HTTPStatus.OK


@blueprint_signature.route("/verify", methods=["POST"])
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
                        signature: 'a1b2c3d4e5f6g7h8i9j0'
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
        tags:
            - signature
    """
    payload = request.get_json()
    # Validate that signature and data are present in payload
    if SignatureFields.signature not in payload or SignatureFields.data not in payload:
        return {"error": "Missing signature or data in payload"}, HTTPStatus.BAD_REQUEST

    handler = SignatureHandler(signer=HMACSigner())

    # Generate signature from data and compare to provided signature
    signature = handler.sign(payload[SignatureFields.data])
    if signature != payload[SignatureFields.signature]:
        return {"error": "Invalid signature or data"}, HTTPStatus.BAD_REQUEST
    else:
        return "", HTTPStatus.NO_CONTENT
