import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from utils.hasher import Hasher


class Cryptor:

    @staticmethod
    def encrypt_str(str_: str, password: bytes) -> str:
        salt = os.urandom(16)
        nonce = os.urandom(12)
        key = Hasher.driver_key(password=password, salt=salt)

        aes_gcm = AESGCM(key)
        ciphertext = aes_gcm.encrypt(nonce, str_.encode(), None)

        encrypted_block = salt + nonce + ciphertext
        return base64.b64encode(encrypted_block).decode()

    @staticmethod
    def decrypt_str(str_: str, password: bytes) -> str:
        decoded = base64.b64decode(str_.encode())

        salt = decoded[:16]
        nonce = decoded[16:28]
        ciphertext = decoded[28:]

        key = Hasher.driver_key(password=password, salt=salt)
        aes_gcm = AESGCM(key)
        decrypted = aes_gcm.decrypt(nonce, ciphertext, None)

        return decrypted.decode()
