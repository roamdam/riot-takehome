from unittest import TestCase
from unittest.mock import patch
from http import HTTPStatus

from api.config.fields import SignatureFields
from api.controllers.signature import SignatureHandler
from api.helpers.signer import RootSigner


class TestSignatureHandlerCanonicalise(TestCase):

    def setUp(self):
        self.handler = SignatureHandler(signer=RootSigner())

    def test_canonicalise_returns_same_value_for_equivalent_dicts(self):
        payload1 = {"a": 1, "e": "value", "b": {"c": 4, "d": None}}
        payload2 = {"b": {"d": None, "c": 4}, "a": 1, "e": "value"}

        actual1 = self.handler.canonicalise(payload1)
        actual2 = self.handler.canonicalise(payload2)

        self.assertEqual(actual1, actual2)

    def test_canonicalise_returns_different_values_for_different_dicts(self):
        payload1 = {"a": 1, "b": 2}
        payload2 = {"a": 1, "b": 3}

        actual1 = self.handler.canonicalise(payload1)
        actual2 = self.handler.canonicalise(payload2)

        self.assertNotEqual(actual1, actual2)


class TestSignatureHandlerGenerateSignature(TestCase):

    def setUp(self):
        self.handler = SignatureHandler(signer=RootSigner())

    @patch.object(SignatureHandler, "canonicalise")
    @patch.object(RootSigner, "signature")
    def test_generate_signature_calls_signer(self, mo_signer, mo_canon):
        payload = {}

        actual = self.handler.generate_signature(payload)

        self.assertEqual(actual, mo_signer.return_value)
        mo_canon.assert_called_once_with(payload)
        mo_signer.assert_called_once_with(mo_canon.return_value)

class TestSignatureHandlerMainMethods(TestCase):

    def setUp(self):
        self.handler = SignatureHandler(signer=RootSigner())    

    @patch.object(SignatureHandler, "generate_signature")
    def test_sign_payload_returns_signature_and_OK(self, mo_gen_sig):
        payload = {}

        actual, status = self.handler.sign_payload(payload)
        expected = {
            SignatureFields.signature: mo_gen_sig.return_value
        }

        self.assertDictEqual(actual,expected)
        self.assertEqual(status, HTTPStatus.OK)
        mo_gen_sig.assert_called_once_with(payload)

    @patch.object(SignatureHandler, "generate_signature")
    def test_verify_payload_returns_NOCONTENT_for_valid_payload(self, mo_gen_sig):
        payload = {
            SignatureFields.signature: "signature",
            SignatureFields.data: {}
        }
        mo_gen_sig.return_value = "signature"

        actual, status = self.handler.verify_payload(payload)

        self.assertEqual(actual, "")
        self.assertEqual(status, HTTPStatus.NO_CONTENT)
        mo_gen_sig.assert_called_once_with({})

    @patch.object(SignatureHandler, "generate_signature")
    def test_verify_payload_returns_BADREQUEST_for_invalid_payload(self, mo_gen_sig):
        payload = {
            SignatureFields.signature: "signature",
            SignatureFields.data: {}
        }
        mo_gen_sig.return_value = "tampered"

        _, status = self.handler.verify_payload(payload)

        self.assertEqual(status, HTTPStatus.BAD_REQUEST)
        mo_gen_sig.assert_called_once_with({})
