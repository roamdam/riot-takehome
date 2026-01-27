from unittest import TestCase
from binascii import Error as BinasciiError
from json import JSONDecodeError

from api.helpers.crypters import Base64Crypter


class TestBase64Crypter(TestCase):
    def setUp(self):
        self.crypter = Base64Crypter()

    def test_decrypt_wrong_input(self):
        non_bs64 = "Apple, banana, carrot"

        with self.subTest("BinasciiError is raised on non-base64 input"):
            with self.assertRaises(BinasciiError):
                self.crypter.decrypt(non_bs64)

        with self.subTest("JSONDecodeError is raised on invalid json input"):
            non_json = "ApPl"
            with self.assertRaises((JSONDecodeError, UnicodeDecodeError)):
                self.crypter.decrypt(non_json)
        
        with self.subTest("UnicodeEncodeError is raised on invalid ascii input"):
            non_ascii = "§§"
            with self.assertRaises(UnicodeEncodeError):
                self.crypter.decrypt(non_ascii)

    def test_encrypt_decrypt(self):
        original = {"who": "A man with a name."}
        bs64_repr = "eyJ3aG8iOiAiQSBtYW4gd2l0aCBhIG5hbWUuIn0="

        with self.subTest("Test encryption"):
            actual = self.crypter.encrypt(original)

            self.assertEqual(actual, bs64_repr)

        with self.subTest("Test decryption"):
            actual = self.crypter.decrypt(bs64_repr)

            self.assertDictEqual(actual, original)
