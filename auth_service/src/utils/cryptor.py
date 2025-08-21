import base64
import os

from core.app_config import crypto_config
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from utils.hasher import Hasher


class Cryptor:
    """Utils - шифрование данных."""

    @staticmethod
    def encrypt_str(str_: str, password: str) -> str:
        """
        Шифрование строки.

        @type str_: str
        @param str_:
        @type password: str
        @param password: Мастер-пароль (в открытом виде).

        @rtype: str
        @return:
        """
        salt = os.urandom(crypto_config.salt_length_bytes)
        nonce = os.urandom(crypto_config.nonce_length_bytes)
        key = Hasher.gen_driver_key(password=password, salt=salt)

        aes_gcm = AESGCM(key)
        ciphertext = aes_gcm.encrypt(nonce, str_.encode(), None)

        encrypted_block = salt + nonce + ciphertext
        return base64.b64encode(encrypted_block).decode()

    @staticmethod
    def decrypt_str(str_: str, password: str) -> str:
        """
        Расшифровывание строки.

        @type str_: str
        @param str_:
        @type password: str
        @param password: Мастер-пароль (в открытом виде).

        @rtype: str
        @return:
        """
        decoded = base64.b64decode(str_.encode())

        salt_len = crypto_config.salt_length_bytes
        nonce_len = crypto_config.nonce_length_bytes
        salt = decoded[:salt_len]
        # TODO:
        nonce = decoded[salt_len : salt_len + nonce_len]  # noqa: E203
        ciphertext = decoded[salt_len + nonce_len :]  # noqa: E203

        key = Hasher.gen_driver_key(password=password, salt=salt)
        aes_gcm = AESGCM(key)
        decrypted = aes_gcm.decrypt(nonce, ciphertext, None)

        return decrypted.decode()
