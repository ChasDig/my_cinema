import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core import crypto_config
from utils.hasher import Hasher


class Cryptor:

    @staticmethod
    def encrypt_str(str_: str, password: str) -> str:
        salt = os.urandom(crypto_config.salt_length_bytes)
        nonce = os.urandom(crypto_config.nonce_length_bytes)
        key = Hasher.gen_driver_key(password=password, salt=salt)

        aes_gcm = AESGCM(key)
        ciphertext = aes_gcm.encrypt(nonce, str_.encode(), None)

        encrypted_block = salt + nonce + ciphertext
        return base64.b64encode(encrypted_block).decode()

    @staticmethod
    def decrypt_str(str_: str, password: str) -> str:
        decoded = base64.b64decode(str_.encode())

        salt_len = crypto_config.salt_length_bytes
        nonce_len = crypto_config.nonce_length_bytes
        salt = decoded[:salt_len]
        nonce = decoded[salt_len: salt_len + nonce_len]
        ciphertext = decoded[salt_len + nonce_len:]

        key = Hasher.gen_driver_key(password=password, salt=salt)
        aes_gcm = AESGCM(key)
        decrypted = aes_gcm.decrypt(nonce, ciphertext, None)

        return decrypted.decode()
