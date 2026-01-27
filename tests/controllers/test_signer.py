from unittest import TestCase
from unittest.mock import patch

from api.controllers.signature import SignatureHandler
from api.helpers.signer import RootSigner


class TestSigner(TestCase):

    def setUp(self):
        self.handler = SignatureHandler(signer=RootSigner())

    def test_canonicalise(self):
        payload1 = {"a": 1, "e": "value", "b": {"c": 4, "d": None}}
        payload2 = {"b": {"d": None, "c": 4}, "a": 1, "e": "value"}

        actual1 = self.handler._canonicalise(payload1)
        actual2 = self.handler._canonicalise(payload2)

        self.assertEqual(actual1, actual2)

    def test_canonicalise_variability(self):
        payload1 = {"a": 1, "b": 2}
        payload2 = {"a": 1, "b": 3}

        actual1 = self.handler._canonicalise(payload1)
        actual2 = self.handler._canonicalise(payload2)

        self.assertNotEqual(actual1, actual2)

    # Test signature generation by mocking the signer and the canonical
    @patch.object(SignatureHandler, "_canonicalise")
    @patch.object(RootSigner, "signature")
    def test_sign(self, mo_signer, mo_canon):
        payload = {"key": "value"}

        signature = self.handler.sign(payload)

        self.assertEqual(signature, mo_signer.return_value)
        mo_canon.assert_called_once_with(payload)
        mo_signer.assert_called_once_with(mo_canon.return_value)
