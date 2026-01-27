from unittest import TestCase
from flask import Flask
from http import HTTPStatus

from api.config.fields import SignatureFields
from api.services.signature import sign, verify


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

        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertIn(SignatureFields.signature, response)
        self.assertIsInstance(response[SignatureFields.signature], str)

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

        self.assertEqual(status_code1, HTTPStatus.OK)
        self.assertEqual(status_code2, HTTPStatus.OK)
        self.assertEqual(response1[SignatureFields.signature], response2[SignatureFields.signature])

    def test_roundtrip_verify(self):
        payload = {
            "name": "Bob",
            "role": "admin"
        }

        # Sign the data to get a valid signature
        with mock_app.test_request_context("/sign", method="POST", json=payload):
            sign_response, _ = sign()

        signature = sign_response[SignatureFields.signature]

        # Verify the signed data, this is the actual test
        verify_payload = {
            SignatureFields.data: payload,
            SignatureFields.signature: signature
        }

        with mock_app.test_request_context("/verify", method="POST", json=verify_payload):
            _, verify_status = verify()

        self.assertEqual(verify_status, HTTPStatus.NO_CONTENT)

    def test_unsuccessful_verify(self):
        payload = {
            "name": "Charlie",
            "role": "user"
        }

        # Sign the data to get a valid signature
        with mock_app.test_request_context("/sign", method="POST", json=payload):
            sign_response, _ = sign()

        signature = sign_response[SignatureFields.signature]

        # Subtest 1: Altered signature
        altered_signature_payload = {
            SignatureFields.data: payload,
            SignatureFields.signature: signature[::-1]
        }

        with mock_app.test_request_context("/verify", method="POST", json=altered_signature_payload):
            _, altered_status = verify()

        with self.subTest("Altered Signature"):
            self.assertEqual(altered_status, HTTPStatus.BAD_REQUEST)

        # Subtest 2: Tampered data
        tampered_data_payload = {
            SignatureFields.data: {
                "name": "Charlie",
                "role": "admin"  # changed role
            },
            SignatureFields.signature: signature
        }

        with mock_app.test_request_context("/verify", method="POST", json=tampered_data_payload):
            _, tampered_status = verify()

        with self.subTest("Tampered Data"):
            self.assertEqual(tampered_status, HTTPStatus.BAD_REQUEST)
