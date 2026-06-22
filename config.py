import os

APP_NAME = "可伴桌面"
APP_VERSION = "1.0.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "keban.db")

API_BASE_URL = "https://api.keban.com"
WS_URL = "wss://ws.keban.com"

TEST_VERIFICATION_CODE = "123456"
TEST_DEVICE_SERIAL = "KB-TEST-001"

COLORS = {
    "primary": "#8ED7C4",
    "primary_dark": "#6BC4AE",
    "secondary": "#FFF8F0",
    "accent": "#FF9F6B",
    "accent_dark": "#FF8547",
    "text": "#333333",
    "text_light": "#666666",
    "border": "#E8E8E8",
    "success": "#7DD3A0",
    "error": "#FF6B6B",
    "warning": "#FFD93D",
    "white": "#FFFFFF",
}

FONT_FAMILY = "Microsoft YaHei"
if os.name == "posix":
    FONT_FAMILY = "PingFang SC"
