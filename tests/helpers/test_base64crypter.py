from unittest import TestCase
from unittest.mock import patch

from api.helpers.encryption import Encrypter


class TestEncrypter(TestCase):
    # Set testing class in setup
    def setUp(self):
        self.crypter = Encrypter()

    def test_is_encrypted_true(self):
        with self.subTest("With regular string:"):
            encrypted = self.crypter.SENTINEL + "test"
            self.assertTrue(self.crypter.is_encrypted(encrypted))

        with self.subTest("With empty string:"):
            encrypted = self.crypter.SENTINEL + ""
            self.assertTrue(self.crypter.is_encrypted(encrypted))

    def test_is_encrypted_false(self):
        not_encrypted = "this is not encrypted"
        self.assertFalse(self.crypter.is_encrypted(not_encrypted))

    def test_is_encrypted_short_string(self):
        with self.subTest("With short string"):
            not_encrypted = self.crypter.SENTINEL[:-1]  # Provides a shorter string without IndexError risk
            self.assertFalse(self.crypter.is_encrypted(not_encrypted))

    def test_remove_sentinel_ok(self):
        encrypted = self.crypter.SENTINEL + "test"

        actual = self.crypter._remove_sentinel(encrypted)
        expected = "test"

        self.assertEqual(actual, expected)

    def test_remove_sentinel_too_short(self):
        # If called on a too short string, will return an empty string
        s = self.crypter.SENTINEL[:-1]

        actual = self.crypter._remove_sentinel(s)

        self.assertEqual(actual, "")

    def test_encrypt_decrypt(self):
        test_values = {
            "str": "hello world",
            "int": 12345,
            "list": ["a", "b", "c"],
            "dict": {"key": "value", "num": 42},
            "none": None,
            "bool": True
        }

        for key, value in test_values.items():
            with self.subTest(f"Testing encrypt and decrypt for type {key}:"):
                encrypted = self.crypter.encrypt(value)
                self.assertIsInstance(encrypted, str, f"Encrypted value for {key} should be a string.")
                self.assertTrue(self.crypter.is_encrypted(encrypted), f"Encrypted value for {key} should be recognized as encrypted.")

                decrypted = self.crypter.decrypt(encrypted)
                self.assertEqual(decrypted, value, f"Decrypted value for {key} should match the original.")
