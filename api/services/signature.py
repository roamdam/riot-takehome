from flask import Blueprint


blueprint_signature = Blueprint("signature", import_name="__name__")


@blueprint_signature.route("/sign", methods=["POST"])
def sign():
    """
    Sign

    ---
    tags:
        - Signature
    post:
        summary: Encrypt a JSON object
        description: Encrypts all depth-1 values of the provided JSON object.
    """
    return {}, 200

@blueprint_signature.route("/verify", methods=["POST"])
def verify():
    """
    Verify

    ---
    tags:
        - Signature
    post:
        summary: Encrypt a JSON object
        description: Encrypts all depth-1 values of the provided JSON object.
    """
    return {}, 200
