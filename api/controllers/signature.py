import json
from logging import getLogger

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

    def _canonicalise(self, payload: dict) -> str:
        """Create a canonical string representation of the json payload.

        :param dict payload: The input payload validated as JSON object
        """
        return json.dumps(payload, separators=(",", ":"), indent=None, sort_keys=True, ensure_ascii=False)

    def sign(self, payload: dict) -> str:
        """Generate string signature of payload.

        :param dict payload: The input payload validated as JSON object

        The generated signature is independent of the keys order.
        """
        self.logger.debug("Generate signature for payload %s", payload)
        canonical = self._canonicalise(payload)
        return self.signer.signature(canonical)
