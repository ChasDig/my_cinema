import base64
import hashlib
import hmac
import os

from core.app_config import crypto_config
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Hasher:
    """Utils - хеширование данных."""

    password_template = "{iter}{delimiter}{salt}{delimiter}{password_hash_str}"

    @staticmethod
    def gen_driver_key(password: str, salt: bytes) -> bytes:
        """
        Хеширование пароля благодаря функции формирования ключа PBKDF2-HMAC.

        @type password: str
        @param password: Мастер-пароль (в открытом виде).
        @type salt: bytes
        @param salt: Соль.

        @rtype: bytes
        @return:
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=crypto_config.length_hash,
            salt=salt,
            iterations=crypto_config.count_iter,
        )

        return kdf.derive(password.encode())

    @classmethod
    def gen_password_hash(
        cls,
        password: str,
        salt: bytes | None = None,
        count_iter: int | None = None,
    ) -> str:
        """
        Генерирование hash-пароля.

        @type password: str
        @param password: Мастер-пароль (в открытом виде).
        @type salt: bytes | None
        @param salt: Соль.
        @type count_iter: int | None
        @param count_iter: Кол-во итераций для функции формирования ключа.

        @rtype: str
        @return:
        """
        if not salt:
            salt = os.urandom(crypto_config.salt_length_bytes)

        if not count_iter:
            count_iter = crypto_config.count_iter

        password_hash = cls.gen_driver_key(password=password, salt=salt)

        return cls.password_template.format(
            iter=count_iter,
            delimiter=crypto_config.password_delimiter,
            salt=base64.b64encode(salt).decode(),
            password_hash_str=base64.b64encode(password_hash).decode(),
        )

    @classmethod
    def check_password_by_hash(
        cls,
        incoming_password: str,
        user_hash_password: str,
        password_delimiter: str | None = None,
    ) -> bool:
        """
        Проверка паролей (пароля в открытом виде и hash-а) на соответствие.

        @type incoming_password: str
        @param incoming_password: Пароль в открытом виде.
        @type user_hash_password: str
        @param user_hash_password: Hash-пароль.
        @type password_delimiter: str | None
        @param password_delimiter: Разделитель, используемый в hash-пароле.

        @rtype: bool
        @return:
        """
        if password_delimiter is None:
            password_delimiter = crypto_config.password_delimiter

        count_iter, salt, hash_password = user_hash_password.split(
            password_delimiter,
        )
        incoming_hash_password = cls.gen_password_hash(
            password=incoming_password,
            count_iter=int(count_iter),
            salt=base64.b64decode(salt),
        )

        return True if user_hash_password == incoming_hash_password else False

    @staticmethod
    def hash_str(str_: str, password: str) -> str:
        """
        Хеширование строки.

        @type str_: str
        @param str_:
        @type password: str
        @param password: Пароль в открытом виде.

        @rtype: str
        @return:
        """
        normalize_str = str_.lower().strip()

        return hmac.new(
            password.encode(),
            normalize_str.encode(),
            hashlib.sha256,
        ).hexdigest()
