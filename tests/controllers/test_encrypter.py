from unittest import TestCase
from unittest.mock import patch

from api.controllers.encryption import EncryptionHandler
from api.helpers.crypters import RootCrypter


class TestEncrypter(TestCase):
    # Set testing class in setup
    def setUp(self):
        self.handler = EncryptionHandler(crypter=RootCrypter())

    def test_is_encrypted_true(self):
        with self.subTest("With regular string:"):
            encrypted = self.handler.SENTINEL + "test"
            self.assertTrue(self.handler.is_encrypted(encrypted))

        with self.subTest("With empty string:"):
            encrypted = self.handler.SENTINEL + ""
            self.assertTrue(self.handler.is_encrypted(encrypted))

    def test_is_encrypted_false(self):
        not_encrypted = "this is not encrypted"
        self.assertFalse(self.handler.is_encrypted(not_encrypted))

    def test_is_encrypted_short_string(self):
        with self.subTest("With short string"):
            not_encrypted = self.handler.SENTINEL[:-1]  # Provides a shorter string without IndexError risk
            self.assertFalse(self.handler.is_encrypted(not_encrypted))

    def test_remove_sentinel_ok(self):
        encrypted = self.handler.SENTINEL + "test"

        actual = self.handler._remove_sentinel(encrypted)
        expected = "test"

        self.assertEqual(actual, expected)

    def test_remove_sentinel_too_short(self):
        # If called on a too short string, will return an empty string
        s = self.handler.SENTINEL[:-1]

        actual = self.handler._remove_sentinel(s)

        self.assertEqual(actual, "")

    @patch.object(RootCrypter, "encrypt")
    def test_encrypt(self, mo_crypter):
        value = {"key": "value"}

        actual = self.handler.encrypt(value)
        expected = self.handler.SENTINEL + mo_crypter.return_value

        self.assertEqual(actual, expected)
        mo_crypter.assert_called_once_with(value)

    @patch.object(RootCrypter, "decrypt")
    def test_decrypt(self, mo_crypter):
        encrypted = self.handler.SENTINEL + "encrypted_data"

        actual = self.handler.decrypt(encrypted)
        expected = mo_crypter.return_value

        self.assertEqual(actual, expected)
        mo_crypter.assert_called_once_with("encrypted_data")
