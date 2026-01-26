from typing import Any

from ..helpers.crypters import RootCrypter


class CryptingHandler:
    SENTINEL = "@@enc@@v1::"

    def __init__(self, crypter: RootCrypter):
        self.crypter = crypter

    def is_encrypted(self, s: str) -> bool:
        """Check if value contains the sentinel marker.
        
        :param s: Encrypted string as received by ``decrypt``
        """
        if len(s) < len(self.SENTINEL):
            return False

        return s.startswith(self.SENTINEL)

    def _remove_sentinel(self, s: str) -> str:
        """Remove sentinel from input string.
        
        :param s: Encrypted string as received by ``decrypt``
        """
        return s[len(self.SENTINEL):]
    
    def encrypt(self, value: Any) -> str:
        """Apply encryption algorithm and prepend sentinel.
        
        :param value: Any json-serializable value
        """
        return self.SENTINEL + self.crypter.encrypt(value)
            
    def decrypt(self, s: str) -> Any:
        """Decrypt input string by removing sentinel then deciphering.
        
        :param s: Encrypted string as received by ``decrypt``
        """
        encrypted = self._remove_sentinel(s)
        return self.crypter.decrypt(encrypted)
