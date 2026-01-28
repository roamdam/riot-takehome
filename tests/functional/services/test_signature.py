from unittest import TestCase
from unittest.mock import patch
from http import HTTPMethod, HTTPStatus
from flask import Flask

from api.config.fields import SignatureFields
from api.controllers.signature import SignatureHandler
from api.services.signature import sign, verify


mock_app = Flask(__name__)


class TestSignEndpoint(TestCase):

    def test_sign_returns_signature_and_OK(self):
        payload = {}

        with mock_app.test_request_context("/sign", method=HTTPMethod.POST, json=payload):
            response, status_code = sign()

        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertIn(SignatureFields.signature, response.keys())
        self.assertEqual(len(response.keys()), 1)
        self.assertIsInstance(response[SignatureFields.signature], str)

    @patch.object(SignatureHandler, "sign_payload")
    def test_sign_returns_ERROR_on_sign_error(self, mo_sign):
        payload = {}
        mo_sign.side_effect = ValueError

        with mock_app.test_request_context("/sign", method=HTTPMethod.POST, json=payload):
            _, status_code = sign()

        self.assertEqual(status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    def test_sign_returns_BADREQUEST_on_invalid_input(self):
        # With invalid JSON, get_json(silent=True) will return None
        with mock_app.test_request_context("/sign", method=HTTPMethod.POST, json=None):
            _, status_code = sign()

        self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)


class TestVerifyEndpoint(TestCase):

    def test_verify_successfully_verifies_payload_signed_by_us(self):
        original = {}

        # First, sign the payload
        with mock_app.test_request_context("/sign", method=HTTPMethod.POST, json=original):
            signed, _ = sign()

        # Second, prepare payload for verify
        payload = {
            SignatureFields.data: original,
            SignatureFields.signature: signed[SignatureFields.signature]
        }

        # This is the actual test : trying to verify our own signed output
        with mock_app.test_request_context("/verify", method=HTTPMethod.POST, json=payload):
            verified, status_code = verify()

        self.assertEqual(status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(verified, "")

    def test_verify_successfully_verifies_equivalent_payloads(self):
        original1 = {
            "drink": "coffee",
            "status": {
                "temperature": "cold",
                "sugar": False
            }
        }
        original2 = {
            "status": {
                "sugar": False,
                "temperature": "cold"
            },
            "drink": "coffee"
        }

        # First, sign one of the payload to get the signature
        with mock_app.test_request_context("/sign", method=HTTPMethod.POST, json=original1):
            signed, _ = sign()

        # Second, prepare payloads for verify
        payload1 = {
            SignatureFields.data: original1,
            SignatureFields.signature: signed[SignatureFields.signature]
        }
        payload2 = {
            SignatureFields.data: original2,
            SignatureFields.signature: signed[SignatureFields.signature]
        }

        # This is the actual test : we should accept both payloads
        with mock_app.test_request_context("/verify", method=HTTPMethod.POST, json=payload1):
            _, status1 = verify()
        with mock_app.test_request_context("/verify", method=HTTPMethod.POST, json=payload2):
            _, status2 = verify()

        self.assertEqual(status1, status2)
        self.assertEqual(status1, HTTPStatus.NO_CONTENT)

    def test_verify_successfully_detect_tampered_payload(self):
        original = {"name": "John"}

        # First, sign the payload
        with mock_app.test_request_context("/sign", method=HTTPMethod.POST, json=original):
            signed, _ = sign()

        # Second, prepare payload for verify
        payload = {
            SignatureFields.data: {"name": "James"},
            SignatureFields.signature: signed[SignatureFields.signature]
        }

        # This is the actual test : verify should return a BAD REQUEST due to tampered data
        with mock_app.test_request_context("/verify", method=HTTPMethod.POST, json=payload):
            _, status_code = verify()

        self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)

    def test_verify_successfully_detect_invalid_signature(self):
        original = {}

        # First, sign the payload
        with mock_app.test_request_context("/sign", method=HTTPMethod.POST, json=original):
            signed, _ = sign()

        # Second, prepare payload for verify
        payload = {
            SignatureFields.data: {},
            SignatureFields.signature: signed[SignatureFields.signature][:-1]
        }

        # This is the actual test : verify should return a BAD REQUEST due to invalid signature
        with mock_app.test_request_context("/verify", method=HTTPMethod.POST, json=payload):
            _, status_code = verify()

        self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)

    def test_verify_returns_BADREQUEST_on_invalid_input(self):
        with self.subTest("Test invalid JSON-dict"):
            # Mock an invalid json input with json=""
            with mock_app.test_request_context("/verify", method=HTTPMethod.POST, json=""):
                _, status_code = verify()

            self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)

        with self.subTest("Test missing keys"):
            payload = {}
            with mock_app.test_request_context("/verify", method=HTTPMethod.POST, json=payload):
                _, status_code = verify()

            self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)

    @patch.object(SignatureHandler, "verify_payload")
    def test_verify_returns_ERROR_on_execution_error(self, mo_verify):
        payload = {
            SignatureFields.data: {},
            SignatureFields.signature: ""
        }
        mo_verify.side_effect = ValueError

        with mock_app.test_request_context("/verify", method=HTTPMethod.POST, json=payload):
            _, status_code = verify()

        self.assertEqual(status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
