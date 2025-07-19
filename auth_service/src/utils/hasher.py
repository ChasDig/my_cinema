import hmac
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


from core import crypto_config


class Hasher:

    @staticmethod
    def driver_key(password: bytes, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=crypto_config.length_hash,
            salt=salt,
            iterations=crypto_config.count_iter,
        )

        return kdf.derive(password)

    @staticmethod
    def hash_str(str_: str, password: bytes) -> str:
        normalize_str = str_.lower().strip()

        return hmac.new(
            password,
            normalize_str.encode(),
            hashlib.sha256,
        ).hexdigest()
