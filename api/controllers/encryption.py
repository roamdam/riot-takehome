from typing import Any

from ..helpers.crypters import RootCrypter


class CryptingHandler:
    """The CryptingHandler is responsible for high-level management of encryption and decryption of values.

    The encryption/decryption process is handled by the provided ``crypter`` so that the handler remains agnostic of
    the algorithm used. When crypting a value, the handler prepends a sentinel marker to the encrypted string so as to
    be able to identify it back as crypted.

    When asked to decrypt a value, it removes the marker then delegates the decryption to the crypter.

    param crypter: An instance of a class inheriting from ``RootCrypter``, containing `encrypt` and `decrypt` methods.
    """
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
