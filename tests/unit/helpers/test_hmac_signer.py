from unittest import TestCase

from api.helpers.signer import HMACSigner


class TestHMACSigner(TestCase):
    def setUp(self):
        self.signer = HMACSigner()

    def test_signature_is_str_with_correct_length(self):
        message = "How is my signature ?"
        signature = self.signer.signature(message)
        self.assertIsInstance(signature, str)
        self.assertEqual(len(signature), 64)  # Length of SHA256 hex digest

    def test_signature_is_deterministic_and_different_for_different_inputs(self):
        message1 = "Handwavy"
        message2 = "Pinacle aesthetic"

        with self.subTest("Same message provides same signature"):
            signature1 = self.signer.signature(message1)
            signature2 = self.signer.signature(message1)
            self.assertEqual(signature1, signature2)

        with self.subTest("Different messages provide different signatures"):
            signature3 = self.signer.signature(message2)
            self.assertNotEqual(signature1, signature3)
