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

        nonce_s, nonce_e = (
            crypto_config.salt_length_bytes,
            crypto_config.nonce_length_bytes,
        )
        nonce = decoded[nonce_s:nonce_e]
        salt = decoded[:crypto_config.salt_length_bytes]
        ciphertext = decoded[crypto_config.nonce_length_bytes:]

        key = Hasher.gen_driver_key(password=password, salt=salt)
        aes_gcm = AESGCM(key)
        decrypted = aes_gcm.decrypt(nonce, ciphertext, None)

        return decrypted.decode()
