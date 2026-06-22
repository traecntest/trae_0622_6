import asyncio
import json
import random
import time
from PySide6.QtCore import QObject, Signal, QTimer
from config import WS_URL


class WebSocketClient(QObject):
    message_received = Signal(dict)
    connected = Signal()
    disconnected = Signal()
    device_status_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connected_flag = False
        self.mock_mode = True
        self.mock_timer = QTimer(self)
        self.mock_timer.timeout.connect(self._mock_tick)
        self.emotions = ["happy", "thinking", "sleepy", "curious", "excited"]

    def connect(self):
        if self.mock_mode:
            QTimer.singleShot(500, self._mock_connect)
        else:
            asyncio.create_task(self._real_connect())

    def disconnect(self):
        if self.mock_mode:
            self.mock_timer.stop()
            self.connected_flag = False
            self.disconnected.emit()

    def _mock_connect(self):
        self.connected_flag = True
        self.connected.emit()
        self.mock_timer.start(3000)

    def _mock_tick(self):
        status = {
            "online": True,
            "battery": max(10, random.randint(70, 100) - int(time.time() * 0.001) % 30),
            "signal": random.randint(3, 5),
            "emotion": random.choice(self.emotions),
            "brightness": 70,
            "volume": 60
        }
        self.device_status_changed.emit(status)

        if random.random() < 0.1:
            self.message_received.emit({
                "id": int(time.time()),
                "sender": "child",
                "content": random.choice([
                    "妈妈，我想你了！",
                    "今天的任务我完成啦！",
                    "机器人给我讲了个故事",
                    "我学会了一首新歌",
                    "😊"
                ]),
                "msg_type": "text",
                "timestamp": int(time.time())
            })

    async def _real_connect(self):
        try:
            async with websockets.connect(WS_URL) as websocket:
                self.connected_flag = True
                self.connected.emit()
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("type") == "device_status":
                        self.device_status_changed.emit(data.get("data", {}))
                    else:
                        self.message_received.emit(data)
        except Exception as e:
            print(f"WebSocket error: {e}")
            self.connected_flag = False
            self.disconnected.emit()

    def send_message(self, content, msg_type="text"):
        if self.mock_mode:
            return {
                "code": 0,
                "data": {
                    "id": int(time.time()),
                    "sender": "parent",
                    "content": content,
                    "msg_type": msg_type,
                    "timestamp": int(time.time())
                }
            }
        return {"code": 0}

    def send_control(self, action, params=None):
        if self.mock_mode:
            return {"code": 0, "message": f"已发送{action}指令"}
        return {"code": 0}

    def is_connected(self):
        return self.connected_flag
