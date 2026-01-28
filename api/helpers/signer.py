from hashlib import sha256
import hmac
from logging import getLogger

from ..config.settings import HMAC_SECRET


class RootSigner:
    """Root class for signing algorithms classes."""

    def signature(self, s: str) -> str:
        """Generate signature for input `s`.

        To be overridden in child classes.
        """
        pass


class HMACSigner(RootSigner):
    """Implement HMAC signing algorithm."""
    ENCODING = "utf-8"

    def __init__(self):
        self.logger = getLogger(__name__)
        if not HMAC_SECRET:
            self.logger.warning("HMAC_SECRET is not set, signature algorithm is vulnerable.")

    def signature(self, message: str) -> str:
        """Create an HMAC-SHA256 signature of a message as an hexadecimal string.

        :param str message: The message to sign
        """
        message_bytes = message.encode(self.ENCODING)
        secret_bytes = HMAC_SECRET.encode(self.ENCODING)

        return hmac.new(key=secret_bytes, msg=message_bytes, digestmod=sha256).hexdigest()
