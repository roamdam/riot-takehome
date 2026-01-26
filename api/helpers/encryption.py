from base64 import standard_b64encode, standard_b64decode
import json
from logging import getLogger
from typing import Any


class Encrypter:
    SENTINEL = "@@enc@@v1::"

    def __init__(self):
        super().__init__()
        self.logger = getLogger(__name__)

    def encrypt(self, value: Any) -> str:
        return self.SENTINEL + standard_b64encode(json.dumps(value, ensure_ascii=False).encode("utf-8")).decode("ascii")
            
    def is_encrypted(self, s: str) -> bool:
        """Check if value contains the sentinel marker."""
        if len(s) < len(self.SENTINEL):
            return False

        return s.startswith(self.SENTINEL)
    
    def decrypt(self, s: str) -> Any:
        encrypted = self._remove_sentinel(s)
        return json.loads(standard_b64decode(encrypted.encode("ascii")))

    def _remove_sentinel(self, s: str) -> str:
        """Remove sentinel from value."""
        return s[len(self.SENTINEL):]
