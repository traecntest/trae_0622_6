from cryptography.fernet import Fernet
import base64
import hashlib
import os


def get_key():
    key_path = os.path.join(os.path.dirname(__file__), ".key")
    if os.path.exists(key_path):
        with open(key_path, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, "wb") as f:
            f.write(key)
        try:
            os.chmod(key_path, 0o600)
        except:
            pass
        return key


def encrypt(data: str) -> str:
    f = Fernet(get_key())
    return f.encrypt(data.encode()).decode()


def decrypt(data: str) -> str:
    f = Fernet(get_key())
    return f.decrypt(data.encode()).decode()


def hash_md5(data: str) -> str:
    return hashlib.md5(data.encode()).hexdigest()
