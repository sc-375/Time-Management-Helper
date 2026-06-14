"""AES-256-GCM encryption for sensitive config values."""
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from ..config import SECRET_KEY


def _get_key() -> bytes:
    """Derive a 32-byte key from SECRET_KEY."""
    key = SECRET_KEY.encode("utf-8")
    if len(key) < 32:
        key = key.ljust(32, b"\x00")
    return key[:32]


def encrypt(plain_text: str) -> str:
    """Encrypt a string with AES-256-GCM. Returns base64-encoded ciphertext+nonce."""
    aesgcm = AESGCM(_get_key())
    nonce = os.urandom(12)
    cipher_bytes = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
    combined = nonce + cipher_bytes
    return base64.b64encode(combined).decode("utf-8")


def decrypt(cipher_text: str) -> str | None:
    """Decrypt a base64-encoded ciphertext+nonce. Returns None if tampered."""
    try:
        aesgcm = AESGCM(_get_key())
        combined = base64.b64decode(cipher_text.encode("utf-8"))
        nonce, cipher_bytes = combined[:12], combined[12:]
        return aesgcm.decrypt(nonce, cipher_bytes, None).decode("utf-8")
    except Exception:
        return None
