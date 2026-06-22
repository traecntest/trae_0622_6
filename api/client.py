import requests
import json
from config import API_BASE_URL


class APIClient:
    def __init__(self, token=None):
        self.base_url = API_BASE_URL
        self.token = token
        self.session = requests.Session()

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = self.session.get(url, headers=self._headers(), timeout=10)
            elif method == "POST":
                response = self.session.post(url, headers=self._headers(), json=data, timeout=10)
            elif method == "PUT":
                response = self.session.put(url, headers=self._headers(), json=data, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, headers=self._headers(), timeout=10)
            return response.json()
        except:
            return self._mock_response(method, endpoint, data)

    def _mock_response(self, method, endpoint, data):
        if endpoint == "/auth/send_code":
            return {"code": 0, "message": "验证码已发送"}
        elif endpoint == "/auth/login":
            return {
                "code": 0,
                "message": "登录成功",
                "data": {
                    "token": "mock_token_" + "x" * 32,
                    "expiry": 3600 * 24 * 7,
                    "user": {
                        "id": 1,
                        "phone": data.get("phone", ""),
                        "child_name": "",
                        "child_age": 0,
                        "device_serial": ""
                    }
                }
            }
        elif endpoint == "/user/bind":
            return {"code": 0, "message": "绑定成功"}
        elif endpoint == "/device/status":
            return {
                "code": 0,
                "data": {
                    "online": True,
                    "battery": 85,
                    "signal": 4,
                    "emotion": "happy",
                    "brightness": 70,
                    "volume": 60
                }
            }
        elif endpoint == "/tasks/list":
            return {
                "code": 0,
                "data": [
                    {"id": 1, "title": "阅读绘本", "description": "读《小王子》第3章", "status": "pending", "reward": "20积分", "due_date": 1782144000},
                    {"id": 2, "title": "数学练习", "description": "完成10道加减法", "status": "completed", "reward": "15积分", "due_date": 1782144000},
                    {"id": 3, "title": "英语跟读", "description": "跟读10个单词", "status": "pending", "reward": "10积分", "due_date": 1782144000}
                ]
            }
        elif endpoint == "/tasks/create":
            return {"code": 0, "message": "任务创建成功", "data": {"id": 999}}
        elif endpoint == "/messages/list":
            return {
                "code": 0,
                "data": [
                    {"id": 1, "sender": "child", "content": "妈妈，我今天在学校很开心！", "msg_type": "text", "timestamp": 1782100000, "is_read": 1},
                    {"id": 2, "sender": "parent", "content": "真棒！今天有什么有趣的事吗？", "msg_type": "text", "timestamp": 1782100100, "is_read": 1},
                    {"id": 3, "sender": "child", "content": "老师表扬我画画好看！😊", "msg_type": "text", "timestamp": 1782100200, "is_read": 1},
                    {"id": 4, "sender": "system", "content": "孩子完成了数学练习任务", "msg_type": "system", "timestamp": 1782110000, "is_read": 0},
                    {"id": 5, "sender": "child", "content": "[语音消息 15秒]", "msg_type": "voice", "timestamp": 1782120000, "is_read": 0}
                ]
            }
        elif endpoint == "/growth/records":
            return {
                "code": 0,
                "data": [
                    {"id": 1, "date": "2026-06-20", "type": "task", "content": "完成阅读任务《小王子》", "mood": 5, "created_at": 1782028800},
                    {"id": 2, "date": "2026-06-20", "type": "chat", "content": "主动分享学校的事情", "mood": 5, "created_at": 1782064800},
                    {"id": 3, "date": "2026-06-21", "type": "task", "content": "完成数学练习", "mood": 4, "created_at": 1782115200},
                    {"id": 4, "date": "2026-06-21", "type": "emotion", "content": "今天心情很好", "mood": 5, "created_at": 1782151200},
                    {"id": 5, "date": "2026-06-22", "type": "chat", "content": "和妈妈聊天很开心", "mood": 5, "created_at": 1782200000}
                ]
            }
        elif endpoint == "/content/subscriptions":
            return {
                "code": 0,
                "data": [
                    {"id": 1, "title": "每日绘本", "description": "每天一个精选绘本故事", "subscribed": True, "icon": "📚"},
                    {"id": 2, "title": "趣味数学", "description": "边玩边学数学知识", "subscribed": True, "icon": "🔢"},
                    {"id": 3, "title": "英语启蒙", "description": "日常英语单词跟读", "subscribed": False, "icon": "🔤"},
                    {"id": 4, "title": "科学探索", "description": "奇妙的科学小实验", "subscribed": False, "icon": "🔬"},
                    {"id": 5, "title": "音乐启蒙", "description": "经典儿歌与音乐欣赏", "subscribed": True, "icon": "🎵"}
                ]
            }
        return {"code": -1, "message": "未知错误"}

    def send_verification_code(self, phone):
        return self._request("POST", "/auth/send_code", {"phone": phone})

    def login(self, phone, code):
        return self._request("POST", "/auth/login", {"phone": phone, "code": code})

    def bind_child(self, child_name, child_age, device_serial):
        return self._request("POST", "/user/bind", {
            "child_name": child_name,
            "child_age": child_age,
            "device_serial": device_serial
        })

    def get_device_status(self):
        return self._request("GET", "/device/status")

    def get_tasks(self):
        return self._request("GET", "/tasks/list")

    def create_task(self, title, description, reward, due_date):
        return self._request("POST", "/tasks/create", {
            "title": title,
            "description": description,
            "reward": reward,
            "due_date": due_date
        })

    def get_messages(self):
        return self._request("GET", "/messages/list")

    def get_growth_records(self):
        return self._request("GET", "/growth/records")

    def get_subscriptions(self):
        return self._request("GET", "/content/subscriptions")
