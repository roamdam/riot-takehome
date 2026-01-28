from http import HTTPStatus
import json
from logging import getLogger
from typing import Tuple, Union

from ..config.fields import SignatureFields
from ..helpers.signer import RootSigner


class SignatureHandler:
    """The SignatureHandler is responsible for generating signatures for JSON payloads.

    The signature algorithm is handled by the provided `signer`, so that the handler remains agnostic of
    the algorithm used.

    :param RootSigner signer: An instance of a class inheriting from `RootSigner`, containing a `signature` method.
    """

    def __init__(self, signer: RootSigner):
        self.signer = signer
        self.logger = getLogger(__name__)

    def canonicalise(self, payload: dict) -> str:
        """Create a canonical string representation of the json payload.

        :param dict payload: The input payload validated as JSON object
        """
        return json.dumps(payload, separators=(",", ":"), indent=None, sort_keys=True, ensure_ascii=False)

    def generate_signature(self, payload: dict) -> str:
        """Generate string signature of payload.

        :param dict payload: The input payload validated as JSON object

        The generated signature is independent of the keys order.
        """
        self.logger.debug("Generate signature for payload %s", payload)
        canonical = self.canonicalise(payload)
        return self.signer.signature(canonical)

    def sign_payload(self, payload: dict) -> Tuple[dict, HTTPStatus]:
        """Generate the signature and prepare Flask response.

        :param dict payload: Any JSON validated payload

        :return: A tuple containing the result and the corresponding OK http status for flask response
        """
        output = {
            SignatureFields.signature: self.generate_signature(payload)
        }
        return output, HTTPStatus.OK

    def verify_payload(self, payload: dict) -> Tuple[Union[str, dict], HTTPStatus]:
        """Verify the data given against the signature.

        Generate the signature from `data`, and compare to the given `signature`. If they match, an empty string
        is returned with a NO CONTENT response. If they don't, a BAD REQUEST is returned.

        :param dict payload: The payload containing `data` and `signature` fields

        :return: A tuple containing the result and the corresponding OK http status for flask response
        """
        signature = self.generate_signature(payload[SignatureFields.data])
        if signature != payload[SignatureFields.signature]:
            return {"error": "Invalid signature or data"}, HTTPStatus.BAD_REQUEST
        else:
            return "", HTTPStatus.NO_CONTENT
