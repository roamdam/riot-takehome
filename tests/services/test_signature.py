from unittest import TestCase

from flask import Flask

from api.config.fields import SignatureFields
from api.services.signature import sign


mock_app = Flask(__name__)


class TestSignatureService(TestCase):

    def test_sign_service(self):
        payload = {
            "name": "Alice",
            "age": 30,
            "city": "Wonderland"
        }

        with mock_app.test_request_context("/sign", method="POST", json=payload):
            response, status_code = sign()

        self.assertEqual(status_code, 200)
        self.assertIn(SignatureFields.signature, response)
        self.assertIsInstance(response[SignatureFields.signature], str)

    # Test exact same output for same canonical payloads
    def test_sign_service_determinism(self):
        payload1 = {
            "b": 2,
            "a": {
                "c": "here",
                "d": "None"
            }
        }
        payload2 = {
            "a": {
                "d": "None",
                "c": "here"
            },
            "b": 2
        }

        with mock_app.test_request_context("/sign", method="POST", json=payload1):
            response1, status_code1 = sign()

        with mock_app.test_request_context("/sign", method="POST", json=payload2):
            response2, status_code2 = sign()

        self.assertEqual(status_code1, 200)
        self.assertEqual(status_code2, 200)
        self.assertEqual(response1[SignatureFields.signature], response2[SignatureFields.signature])
