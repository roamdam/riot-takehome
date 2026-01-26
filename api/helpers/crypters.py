from base64 import standard_b64encode, standard_b64decode
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
        return standard_b64encode(json.dumps(s, ensure_ascii=False).encode("utf-8")).decode("ascii")

    def decrypt(self, s: str) -> Any:
        """Decipher string input using base64 decoding and return as a json object.
        
        :param s: base64-encoded string
        """
        return json.loads(standard_b64decode(s.encode("ascii")))
