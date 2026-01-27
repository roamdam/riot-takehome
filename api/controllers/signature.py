import json
from logging import getLogger

from ..helpers.signer import RootSigner


class SignatureHandler:

    def __init__(self, signer: RootSigner):
        self.signer = signer
        self.logger = getLogger(__name__)

    def _canonicalise(self, payload: dict) -> str:
        """Create a canonical string representation of the json payload.
        
        :param payload: The input payload validated as JSON object

        :return: Canonical string representation, utf-8 encoded.
        """
        return json.dumps(payload, separators=(",", ":"), indent=None, sort_keys=True, ensure_ascii=False)

    def sign(self, payload: dict) -> str:
        self.logger.debug("Generate signature for payload %s", payload)
        canonical = self._canonicalise(payload)
        return self.signer.signature(canonical)
