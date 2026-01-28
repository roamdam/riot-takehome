from unittest import TestCase
from unittest.mock import patch
from http import HTTPStatus

from api.controllers.encryption import EncryptionHandler
from api.helpers.crypters import RootCrypter


class TestEncrypterDetectCryptingMethod(TestCase):

    def setUp(self):
        self.handler = EncryptionHandler(crypter=RootCrypter())

    def test_detect_encrypted_returns_false_and_string_for_too_short_string(self):
        message = "abc"

        is_encrypted, string_value = self.handler.detect_encrypted_string(message)

        self.assertFalse(is_encrypted)
        self.assertEqual(string_value, message)

    def test_detect_encrypted_returns_false_and_string_for_string_without_sentinel(self):
        message = "I'm a long sentence but I don't have a sentinel to guide me."

        is_encrypted, string_value = self.handler.detect_encrypted_string(message)

        self.assertFalse(is_encrypted)
        self.assertEqual(string_value, message)

    def test_detect_encrypted_returns_true_and_cropped_string_for_encrypted_input(self):
        message = self.handler.SENTINEL + "not alone anymore"

        is_encrypted, string_value = self.handler.detect_encrypted_string(message)

        self.assertTrue(is_encrypted)
        self.assertEqual(string_value, "not alone anymore")


class TestEncrypterEndpointMethods(TestCase):

    def setUp(self):
        self.handler = EncryptionHandler(crypter=RootCrypter())

    @patch.object(RootCrypter, "encrypt")
    def test_encrypt_payload_returns_crypted_payload_and_status(self, mo_crypter):
        value = {"key": {}}

        actual, status = self.handler.encrypt_payload(value)
        expected = {
            "key": self.handler.SENTINEL + mo_crypter.return_value
        }

        self.assertDictEqual(actual, expected)
        self.assertEqual(status, HTTPStatus.OK)
        mo_crypter.assert_called_once_with({})

    @patch.object(RootCrypter, "decrypt")
    def test_decrypt_payload_returns_decrypted_on_crypted_input(self, mo_decrypter):
        encrypted = {
            "key": self.handler.SENTINEL + "encrypted data"
        }

        actual, status = self.handler.decrypt_payload(encrypted)
        expected = {
            "key": mo_decrypter.return_value
        }

        self.assertEqual(actual, expected)
        self.assertEqual(status, HTTPStatus.OK)
        mo_decrypter.assert_called_once_with("encrypted data")
    
    @patch.object(RootCrypter, "decrypt")
    def test_decrypt_payload_returns_input_on_clear_input(self, mo_decrypter):
        encrypted = {
            "key": "clear data"
        }

        actual, status = self.handler.decrypt_payload(encrypted)
        expected = {"key": "clear data"}

        self.assertEqual(actual, expected)
        self.assertEqual(status, HTTPStatus.OK)
        mo_decrypter.assert_not_called()
    
    @patch.object(RootCrypter, "decrypt")
    def test_decrypt_payload_returns_input_on_non_str_input(self, mo_decrypter):
        encrypted = {
            "key": {}
        }

        actual, status = self.handler.decrypt_payload(encrypted)
        expected = {"key": {}}

        self.assertEqual(actual, expected)
        self.assertEqual(status, HTTPStatus.OK)
        mo_decrypter.assert_not_called()
