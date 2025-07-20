import os
import base64
import hmac
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


from core import crypto_config


class Hasher:
    password_template = "{iter}{delimiter}{salt}{delimiter}{password_hash_str}"

    @staticmethod
    def gen_driver_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=crypto_config.length_hash,
            salt=salt,
            iterations=crypto_config.count_iter,
        )

        return kdf.derive(password.encode())

    @classmethod
    def gen_password_hash(cls, password: str, salt: bytes = None) -> str:
        if not salt:
            salt = os.urandom(crypto_config.salt_length_bytes)

        password_hash = cls.gen_driver_key(password=password, salt=salt)

        return cls.password_template.format(
            iter=crypto_config.count_iter,
            delimiter=crypto_config.password_delimiter,
            salt=base64.b64encode(salt).decode(),
            password_hash_str=base64.b64encode(password_hash).decode(),
        )

    @staticmethod
    def hash_str(str_: str, password: str) -> str:
        normalize_str = str_.lower().strip()

        return hmac.new(
            password.encode(),
            normalize_str.encode(),
            hashlib.sha256,
        ).hexdigest()
