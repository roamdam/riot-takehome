from binascii import Error as BinasciiError
from http import HTTPStatus
from json import JSONDecodeError
from logging import getLogger
from typing import Tuple

from ..helpers.crypters import RootCrypter


class EncryptionHandler:
    """The CryptingHandler is responsible for high-level management of encryption and decryption of values.

    The encryption/decryption process is handled by the provided ``crypter`` so that the handler remains agnostic of
    the algorithm used. When crypting a value, the handler prepends a sentinel marker to the encrypted string so as to
    be able to identify it back as crypted.

    When asked to decrypt a value, it removes the marker then delegates the decryption to the crypter.

    :param RootCrypter crypter: An instance of a class inheriting from `RootCrypter`, containing `encrypt`
    and `decrypt` methods.
    """
    SENTINEL = "--- BEGIN CRYPTED MESSAGE ---"

    def __init__(self, crypter: RootCrypter):
        self.crypter = crypter
        self.logger = getLogger(__name__)

    def detect_encrypted_string(self, s: str) -> Tuple[bool, str]:
        """Check if the input has a sentinel and return the appropriate string.

        :param str s: Possibly encrypted string as received by ``decrypt`` endpoint

        If the input contains the sentinel, it will be recognized a encrypted. In that case,
        the method returns a tuple `True, <string-without-sentinel>`.

        If the input is clear, it returns a tuple `False, <input string>`.
        """
        if len(s) < len(self.SENTINEL) or not s.startswith(self.SENTINEL):
            return False, s
        else:
            return True, s[len(self.SENTINEL):]

    def encrypt_payload(self, payload: dict) -> Tuple[dict, HTTPStatus]:
        """Encrypt first-level items of input dictionary.

        :param dict payload: JSON input to encrypt

        :return: A tuple containing the result and the corresponding http status for flask response
        """
        encrypted = {}
        for key, value in payload.items():
            encrypted[key] = self.SENTINEL + self.crypter.encrypt(value)
        return encrypted, HTTPStatus.OK

    def decrypt_payload(self, payload: dict) -> Tuple[dict, HTTPStatus]:
        """Decrypt first-level items of input dictionary.

        The method detects encrypted value with the presence of the sentinel marker. Non string items and non encrypted
        strings are returned as such. If decryption fails on any encrypted string, a `BAD REQUEST` is returned.

        :param dict payload: JSON input to encrypt

        :return: A tuple containing the result and the corresponding http status for flask response
        """
        decrypted = {}
        for key, value in payload.items():
            if not isinstance(value, str):
                decrypted[key] = value
                continue

            is_encrypted, string_value = self.detect_encrypted_string(value)
            if not is_encrypted:
                decrypted[key] = string_value
                continue

            # At this point we know the value has been encrypted
            try:
                decrypted[key] = self.crypter.decrypt(string_value)
            except (JSONDecodeError, UnicodeDecodeError, BinasciiError, UnicodeEncodeError) as e:
                self.logger.error("Unable to decrypt value for %s: %s", key, repr(e))
                return {"error": "One or more items were not properly encrypted"}, HTTPStatus.BAD_REQUEST
        return decrypted, HTTPStatus.OK
