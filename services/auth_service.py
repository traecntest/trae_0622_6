import time
from utils.crypto import encrypt, decrypt
from api.client import APIClient
from config import TEST_VERIFICATION_CODE


class AuthService:
    def __init__(self, db):
        self.db = db
        self.api_client = APIClient()
        self.current_user = None
        self._load_user()

    def _load_user(self):
        result = self.db.query_one("SELECT id, phone, token, token_expiry, child_name, child_age, device_serial FROM user ORDER BY id DESC LIMIT 1")
        if result:
            self.current_user = {
                "id": result[0],
                "phone": result[1],
                "token": decrypt(result[2]) if result[2] else None,
                "token_expiry": result[3],
                "child_name": result[4],
                "child_age": result[5],
                "device_serial": result[6]
            }
            if self.current_user["token"]:
                self.api_client.token = self.current_user["token"]

    def has_valid_token(self):
        if not self.current_user or not self.current_user["token"]:
            return False
        if self.current_user["token_expiry"] and self.current_user["token_expiry"] < time.time():
            return False
        return True

    def send_verification_code(self, phone):
        return self.api_client.send_verification_code(phone)

    def login(self, phone, code):
        if code != TEST_VERIFICATION_CODE:
            return {"code": -1, "message": "验证码错误"}
        
        result = self.api_client.login(phone, code)
        if result.get("code") == 0:
            data = result["data"]
            token_encrypted = encrypt(data["token"])
            expiry = int(time.time()) + data["expiry"]
            
            existing = self.db.query_one("SELECT id FROM user WHERE phone = ?", (phone,))
            if existing:
                self.db.execute(
                    "UPDATE user SET token = ?, token_expiry = ?, updated_at = ? WHERE phone = ?",
                    (token_encrypted, expiry, int(time.time()), phone)
                )
            else:
                self.db.execute(
                    "INSERT INTO user (phone, token, token_expiry, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (phone, token_encrypted, expiry, int(time.time()), int(time.time()))
                )
            
            self._load_user()
        
        return result

    def bind_child(self, child_name, child_age, device_serial):
        result = self.api_client.bind_child(child_name, child_age, device_serial)
        if result.get("code") == 0 and self.current_user:
            self.db.execute(
                "UPDATE user SET child_name = ?, child_age = ?, device_serial = ?, updated_at = ? WHERE id = ?",
                (child_name, child_age, device_serial, int(time.time()), self.current_user["id"])
            )
            self._load_user()
        return result

    def logout(self):
        if self.current_user:
            self.db.execute("UPDATE user SET token = NULL, token_expiry = NULL WHERE id = ?", (self.current_user["id"],))
        self.current_user = None
        self.api_client.token = None

    def is_child_binded(self):
        return self.current_user and self.current_user["child_name"] and self.current_user["device_serial"]
