from unittest import TestCase
from unittest.mock import patch
from http import HTTPMethod, HTTPStatus
from flask import Flask

from api.controllers.encryption import EncryptionHandler
from api.services.encryption import encrypt, decrypt


mock_app = Flask(__name__)


class TestEncryptEndpoint(TestCase):

    def test_encrypt_returns_OK_on_valid_input(self):
        payload = {
            "list": ["a", "b"],
            "none": None,
            "str": "bonjour",
            "int": 12345,
            "empty": {},
            "bool": False
        }

        with mock_app.test_request_context("/encrypt", method=HTTPMethod.POST, json=payload):
            response, status_code = encrypt()

        self.assertEqual(status_code, HTTPStatus.OK)
        for key in payload.keys():
            self.assertIn(key, response)
            self.assertIsInstance(response[key], str)
            self.assertTrue(response[key].startswith(EncryptionHandler.SENTINEL))

    @patch.object(EncryptionHandler, "encrypt_payload")
    def test_encrypt_returns_ERROR_on_encryption_error(self, mo_encrypt):
        payload = {}
        mo_encrypt.side_effect = ValueError

        with mock_app.test_request_context("/encrypt", method=HTTPMethod.POST, json=payload):
            _, status_code = encrypt()

        self.assertEqual(status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    def test_encrypt_returns_BADREQUEST_on_invalid_input(self):
        payload = "not a dict"

        with mock_app.test_request_context("/encrypt", method=HTTPMethod.POST, json=payload):
            _, status_code = encrypt()

        self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)


class TestDecryptionEndpoint(TestCase):

    def test_decrypt_successfully_decrypts_payload_encrypted_by_us(self):
        original = {
            "list": ["a", "b"],
            "none": None,
            "str": "bonjour",
            "int": 12345,
            "empty": {},
            "bool": True
        }
        # First, encrypt the payload
        with mock_app.test_request_context("/encrypt", method=HTTPMethod.POST, json=original):
            encrypted, _ = encrypt()

        # Second, add some clear items (to the encrypted output and also to the original)
        encrypted["clear"] = original["clear"] = "just a regular string"
        encrypted["object"] = original["object"] = {"key": "value"}

        # This is the actual test : trying to decrypt our own encrypted output
        with mock_app.test_request_context("/decrypt", method=HTTPMethod.POST, json=encrypted):
            decrypted, status_code = decrypt()

        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertDictEqual(decrypted, original)

    @patch.object(EncryptionHandler, "decrypt_payload")
    def test_decrypt_returns_ERROR_on_decryption_error(self, mo_decrypt):
        payload = {}
        mo_decrypt.side_effect = ValueError

        with mock_app.test_request_context("/decrypt", method=HTTPMethod.POST, json=payload):
            _, status_code = decrypt()

        self.assertEqual(status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    def test_decrypt_returns_BADREQUEST_on_invalid_input(self):
        payload = "not a dict"

        with mock_app.test_request_context("/decrypt", method=HTTPMethod.POST, json=payload):
            _, status_code = decrypt()

        self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)
