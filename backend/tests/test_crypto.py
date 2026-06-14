"""Tests for crypto utility."""
import os
import sys

# Set SECRET_KEY before importing crypto module
os.environ["SECRET_KEY"] = "test-key-32-chars-long!!!!!!"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Now reload config and crypto to pick up the test key
import importlib
from app import config
importlib.reload(config)
from app.utils import crypto
importlib.reload(crypto)


def test_encrypt_decrypt_roundtrip():
    plain = "my_auth_code_123"
    cipher = crypto.encrypt(plain)
    assert cipher != plain
    assert crypto.decrypt(cipher) == plain


def test_decrypt_detects_tampering():
    cipher = crypto.encrypt("original")
    result = crypto.decrypt(cipher + "tampered")
    assert result is None
