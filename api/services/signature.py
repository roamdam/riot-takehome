from flask import Blueprint, request
from http import HTTPStatus

from ..config.fields import SignatureFields
from ..controllers.signature import SignatureHandler
from ..helpers.signer import HMACSigner


blueprint_signature = Blueprint("signature", import_name="__name__")


@blueprint_signature.route("/sign", methods=["POST"])
def sign():
    """
    Sign

    ---
    post:
        summary: Encrypt a JSON object
        description: Encrypts all depth-1 values of the provided JSON object.
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
    Verify

    ---
    post:
        summary: Encrypt a JSON object
        description: Encrypts all depth-1 values of the provided JSON object.
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
        return {"error": "Invalid signature"}, HTTPStatus.BAD_REQUEST
    else:
        return "", HTTPStatus.NO_CONTENT
