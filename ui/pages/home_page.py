import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QScrollArea, QProgressBar,
                               QGridLayout, QGraphicsOpacityEffect)
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal

from ui.widgets import AnimatedButton, CardWidget, RobotFaceWidget
from ui.styles import get_accent_button_style
from config import COLORS


class HomePage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.tasks = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self._create_welcome_card()
        layout.addWidget(self.welcome_card)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        self._create_robot_card()
        content_layout.addWidget(self.robot_card, 2)

        self._create_tasks_card()
        content_layout.addWidget(self.tasks_card, 3)

        layout.addLayout(content_layout, 1)

        self._create_success_message()

    def _create_welcome_card(self):
        self.welcome_card = CardWidget()
        self.welcome_card.setFixedHeight(120)
        
        layout = QHBoxLayout(self.welcome_card)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(20)

        greeting_layout = QVBoxLayout()
        greeting_layout.setSpacing(4)

        greeting_label = QLabel(self._get_greeting())
        greeting_font = QFont()
        greeting_font.setPointSize(20)
        greeting_font.setBold(True)
        greeting_label.setFont(greeting_font)
        greeting_layout.addWidget(greeting_label)

        child_name = self.main_window.auth_service.current_user.get("child_name") or "宝贝" if self.main_window.auth_service.current_user else "宝贝"
        subtitle_label = QLabel(f"今天也要和{child_name}一起加油哦！💪")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
        greeting_layout.addWidget(subtitle_label)

        layout.addLayout(greeting_layout)
        layout.addStretch()

        stats = [("📚", "已完成任务", "12"), ("⭐", "累计积分", "280"), ("🎯", "连续打卡", "7天")]
        for icon, label, value in stats:
            stat_widget = self._create_stat_item(icon, label, value)
            layout.addWidget(stat_widget)

    def _create_stat_item(self, icon, label, value):
        widget = QFrame()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(2)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {COLORS['primary_dark']};")
        layout.addWidget(value_label)

        label_text = QLabel(label)
        label_text.setAlignment(Qt.AlignCenter)
        label_text.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        layout.addWidget(label_text)

        return widget

    def _create_robot_card(self):
        self.robot_card = CardWidget()
        layout = QVBoxLayout(self.robot_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_label = QLabel("🤖 可伴机器人")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        self.robot_face = RobotFaceWidget()
        self.robot_face.setFixedHeight(220)
        layout.addWidget(self.robot_face)

        emotion_map = {
            "happy": "开心 😊",
            "thinking": "思考中 🤔",
            "sleepy": "困倦 😴",
            "curious": "好奇 🧐",
            "excited": "兴奋 🎉"
        }
        current_emotion = self.main_window.device_status.get("emotion", "happy")
        self.emotion_label = QLabel(f"当前状态: {emotion_map.get(current_emotion, '正常')}")
        self.emotion_label.setAlignment(Qt.AlignCenter)
        self.emotion_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
        layout.addWidget(self.emotion_label)

        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(10)

        talk_btn = AnimatedButton("💬 对话")
        talk_btn.clicked.connect(lambda: self.main_window._switch_page(2))
        quick_layout.addWidget(talk_btn)

        call_btn = AnimatedButton("📞 通话")
        call_btn.setStyleSheet(get_accent_button_style())
        call_btn.clicked.connect(self.main_window._start_voice_call)
        quick_layout.addWidget(call_btn)

        layout.addLayout(quick_layout)

        layout.addStretch()

        device_serial = self.main_window.auth_service.current_user.get("device_serial") or "未绑定" if self.main_window.auth_service.current_user else "未绑定"
        serial_label = QLabel(f"设备号: {device_serial}")
        serial_label.setAlignment(Qt.AlignCenter)
        serial_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        layout.addWidget(serial_label)

    def _create_tasks_card(self):
        self.tasks_card = CardWidget()
        layout = QVBoxLayout(self.tasks_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        
        title_label = QLabel("📋 今日任务")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.progress_label = QLabel("0/0 完成")
        self.progress_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px;")
        header_layout.addWidget(self.progress_label)

        add_btn = AnimatedButton("+ 添加")
        add_btn.setFixedSize(70, 32)
        add_btn.setStyleSheet(get_accent_button_style())
        add_btn.clicked.connect(self.main_window._show_task_dialog)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setFrameShape(QFrame.NoFrame)
        self.tasks_scroll.setStyleSheet("background-color: transparent;")

        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(12)
        self.tasks_scroll.setWidget(self.tasks_container)

        layout.addWidget(self.tasks_scroll, 1)

    def _create_task_item(self, task_data):
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary']};
                border-radius: 12px;
            }}
            QFrame:hover {{
                background-color: #F0F7F5;
            }}
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        status = task_data.get("status", "pending")
        is_completed = status == "completed"

        status_btn = QPushButton()
        status_btn.setFixedSize(28, 28)
        status_btn.setCursor(Qt.PointingHandCursor)
        
        if is_completed:
            status_btn.setText("✓")
            status_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['success']};
                    color: white;
                    border: none;
                    border-radius: 14px;
                    font-size: 16px;
                    font-weight: bold;
                }}
            """)
        else:
            status_btn.setText("")
            status_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border: 2px solid {COLORS['border']};
                    border-radius: 14px;
                }}
                QPushButton:hover {{
                    border-color: {COLORS['primary']};
                }}
            """)
            status_btn.clicked.connect(lambda checked, tid=task_data['id']: self._complete_task(tid, item))
        
        layout.addWidget(status_btn)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        title_label = QLabel(task_data.get("title", ""))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        if is_completed:
            title_label.setStyleSheet(f"color: {COLORS['text_light']}; text-decoration: line-through;")
        content_layout.addWidget(title_label)

        desc_label = QLabel(task_data.get("description", ""))
        desc_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        content_layout.addWidget(desc_label)

        layout.addLayout(content_layout, 1)

        reward_label = QLabel(f"🎁 {task_data.get('reward', '')}")
        reward_label.setStyleSheet(f"color: {COLORS['accent_dark']}; font-size: 12px; font-weight: 500;")
        layout.addWidget(reward_label)

        return item

    def _complete_task(self, task_id, item_widget):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "确认完成",
            "确定要标记这个任务为已完成吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for task in self.tasks:
                if task["id"] == task_id:
                    task["status"] = "completed"
                    break
            self._refresh_tasks()

    def _create_success_message(self):
        self.success_msg = QFrame(self)
        self.success_msg.setFixedSize(200, 50)
        self.success_msg.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['success']};
                color: white;
                border-radius: 25px;
            }}
        """)
        self.success_msg.hide()

        msg_layout = QHBoxLayout(self.success_msg)
        msg_layout.setContentsMargins(20, 0, 20, 0)
        
        icon_label = QLabel("✓")
        icon_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        msg_layout.addWidget(icon_label)

        self.success_text = QLabel("操作成功")
        self.success_text.setStyleSheet("color: white; font-size: 14px; font-weight: 500;")
        msg_layout.addWidget(self.success_text)

        self.success_animation = QPropertyAnimation(self.success_msg, b"windowOpacity")
        self.success_animation.setDuration(300)
        self.success_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def show_success_message(self, text):
        self.success_text.setText(text)
        self.success_msg.show()
        self.success_msg.raise_()
        
        center_x = (self.width() - self.success_msg.width()) // 2
        center_y = (self.height() - self.success_msg.height()) // 2
        self.success_msg.move(center_x, center_y)

        self.success_animation.setStartValue(0.0)
        self.success_animation.setEndValue(1.0)
        self.success_animation.start()

        QTimer.singleShot(2000, self._hide_success_message)

    def _hide_success_message(self):
        self.success_animation.setStartValue(1.0)
        self.success_animation.setEndValue(0.0)
        self.success_animation.finished.connect(self.success_msg.hide)
        self.success_animation.start()

    def _get_greeting(self):
        hour = time.localtime().tm_hour
        if hour < 6:
            return "夜深了"
        elif hour < 12:
            return "早上好 ☀️"
        elif hour < 14:
            return "中午好 🌞"
        elif hour < 18:
            return "下午好 🌤️"
        elif hour < 22:
            return "晚上好 🌙"
        else:
            return "夜深了 🌛"

    def load_data(self):
        result = self.main_window.api_client.get_tasks()
        if result.get("code") == 0:
            self.tasks = result.get("data", [])
            self._refresh_tasks()

        emotion = self.main_window.device_status.get("emotion", "happy")
        self.robot_face.set_emotion(emotion)

    def _refresh_tasks(self):
        while self.tasks_layout.count():
            child = self.tasks_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        completed = sum(1 for t in self.tasks if t.get("status") == "completed")
        total = len(self.tasks)
        self.progress_label.setText(f"{completed}/{total} 完成")
        self.progress_bar.setMaximum(total if total > 0 else 1)
        self.progress_bar.setValue(completed)

        for task in self.tasks:
            item = self._create_task_item(task)
            self.tasks_layout.addWidget(item)

        if not self.tasks:
            empty_label = QLabel("🎉 今天还没有任务，点击右上角添加吧！")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px; padding: 40px;")
            self.tasks_layout.addWidget(empty_label)

        self.tasks_layout.addStretch()

    def update_device_status(self, status):
        emotion = status.get("emotion", "happy")
        self.robot_face.set_emotion(emotion)
        emotion_map = {
            "happy": "开心 😊",
            "thinking": "思考中 🤔",
            "sleepy": "困倦 😴",
            "curious": "好奇 🧐",
            "excited": "兴奋 🎉"
        }
        self.emotion_label.setText(f"当前状态: {emotion_map.get(emotion, '正常')}")

    def resizeEvent(self, event):
        if hasattr(self, 'success_msg') and self.success_msg.isVisible():
            center_x = (self.width() - self.success_msg.width()) // 2
            center_y = (self.height() - self.success_msg.height()) // 2
            self.success_msg.move(center_x, center_y)
        super().resizeEvent(event)
