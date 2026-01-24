import base64
import hashlib
import hmac
import os
import time

import jwt

try:
    from passlib.context import CryptContext  # type: ignore
except Exception:  # pragma: no cover
    CryptContext = None

from .config import settings


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") if CryptContext else None


def hash_password(password: str) -> str:
    """Hash password using bcrypt (if available) else PBKDF2-HMAC-SHA256."""
    if _pwd_context is not None:
        return _pwd_context.hash(password)

    iterations = 150_000
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2$%d$%s$%s" % (
        iterations,
        base64.urlsafe_b64encode(salt).decode("ascii").rstrip("="),
        base64.urlsafe_b64encode(dk).decode("ascii").rstrip("="),
    )


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False

    if password_hash.startswith("pbkdf2$"):
        try:
            _, iter_s, salt_s, dk_s = password_hash.split("$", 3)
            iterations = int(iter_s)
            salt = base64.urlsafe_b64decode(salt_s + "==")
            expected = base64.urlsafe_b64decode(dk_s + "==")
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
            return hmac.compare_digest(actual, expected)
        except Exception:
            return False

    if _pwd_context is None:
        return False
    try:
        return _pwd_context.verify(password, password_hash)
    except Exception:
        return False


def create_access_token(subject: int, role: str):
    now = int(time.time())
    payload = {
        "sub": str(subject),
        "role": role,
        "iat": now,
        "exp": now + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def decode_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]) 
