from base64 import b64encode, b64decode
import json
from typing import Any


class RootCrypter:
    """Root class for crypting algorithms classes."""

    def encrypt(self, s: Any) -> str:
        """Encrypt input `s`, return a string.

        To be overridden in child classes.
        """
        pass

    def decrypt(self, s: str) -> Any:
        """Decrypt encryptetd input `s`, return the original object.

        To be overridden in child classes.
        """
        pass


class Base64Crypter(RootCrypter):
    """Implement a base64 obfuscation to mimic encryption."""

    def encrypt(self, s: Any) -> str:
        """Obfuscate json input using base64 encoding.

        :param s: any json-serializable value
        """
        return b64encode(json.dumps(s, ensure_ascii=False).encode("utf-8")).decode("ascii")

    def decrypt(self, s: str) -> Any:
        """Base64 decode string input and return as a json object.

        :param str s: base64-encoded string
        """
        return json.loads(b64decode(s.encode("ascii"), validate=True))
