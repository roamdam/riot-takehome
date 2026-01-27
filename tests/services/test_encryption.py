from unittest import TestCase
from http import HTTPStatus

from flask import Flask

from api.controllers.encryption import CryptingHandler
from api.services.encryption import encrypt, decrypt


mock_app = Flask(__name__)


class TestEncryptionService(TestCase):

    def test_encryption(self):
        payload = {
            "list": ["a", "b"],
            "none": None,
            "str": "bonjour",
            "int": 12345,
            "empty": {},
            "bool": True
        }

        with mock_app.test_request_context("/encrypt", method="POST", json=payload):
            response, status_code = encrypt()

        self.assertEqual(status_code, HTTPStatus.OK)
        for key in payload.keys():
            self.assertIn(key, response)
            self.assertIsInstance(response[key], str)
            self.assertTrue(response[key].startswith(CryptingHandler.SENTINEL))

    def test_decryption(self):
        original = {
            "list": ["a", "b"],
            "none": None,
            "str": "bonjour",
            "int": 12345,
            "empty": {},
            "bool": True
        }
        with mock_app.test_request_context("/encrypt", method="POST", json=original):
            encrypted, _ = encrypt()

        encrypted["clear"] = original["clear"] = "just a regular string"
        encrypted["object"] = original["object"] = {"key": "value"}

        with mock_app.test_request_context("/decrypt", method="POST", json=encrypted):
            decrypted, status_code = decrypt()

        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertDictEqual(decrypted, original)

    def test_decryption_with_invalid_data(self):
        payload = {"invalid": CryptingHandler.SENTINEL + "not a bs64 string"}

        with mock_app.test_request_context("/decrypt", method="POST", json=payload):
            _, status_code = decrypt()

        self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)
