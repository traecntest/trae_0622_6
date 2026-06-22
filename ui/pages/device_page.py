import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QScrollArea, QGridLayout,
                               QDialog, QLineEdit, QTextEdit, QMessageBox,
                               QSpinBox, QComboBox)
from PySide6.QtGui import QColor, QFont, QPainter, QBrush, QPen
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal

from ui.widgets import AnimatedButton, CardWidget, RobotFaceWidget, SwitchButton
from ui.styles import get_accent_button_style, get_ghost_button_style
from config import COLORS


class DevicePage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        self._create_robot_status_card()
        content_layout.addWidget(self.robot_card, 1)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)

        self._create_control_panel()
        right_layout.addWidget(self.control_card)

        self._create_device_settings_card()
        right_layout.addWidget(self.settings_card, 1)

        content_layout.addLayout(right_layout, 1)

        layout.addLayout(content_layout, 1)

        self._create_tasks_list_card()
        layout.addWidget(self.tasks_card, 1)

    def _create_robot_status_card(self):
        self.robot_card = CardWidget()
        layout = QVBoxLayout(self.robot_card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title_label = QLabel("🤖 设备状态")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        self.robot_face = RobotFaceWidget()
        self.robot_face.setFixedHeight(280)
        layout.addWidget(self.robot_face)

        emotion = self.main_window.device_status.get("emotion", "happy")
        emotion_map = {
            "happy": "开心",
            "thinking": "思考中",
            "sleepy": "困倦",
            "curious": "好奇",
            "excited": "兴奋"
        }
        self.status_label = QLabel(f"状态: {emotion_map.get(emotion, '正常')}")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(16)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)

        online = self.main_window.device_status.get("online", False)
        self.online_status = QLabel("● 设备离线" if not online else "● 设备在线")
        self.online_status.setAlignment(Qt.AlignCenter)
        self.online_status.setStyleSheet(f"""
            color: {'#7DD3A0' if online else '#FF6B6B'};
            font-size: 14px;
            font-weight: 500;
        """)
        layout.addWidget(self.online_status)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)

        battery = self.main_window.device_status.get("battery", 0)
        self.battery_stat = self._create_stat_item("🔋", "电量", f"{battery}%")
        stats_grid.addWidget(self.battery_stat, 0, 0)

        signal = self.main_window.device_status.get("signal", 0)
        self.signal_stat = self._create_stat_item("📶", "信号", "强" if signal >= 4 else "中" if signal >= 2 else "弱")
        stats_grid.addWidget(self.signal_stat, 0, 1)

        brightness = self.main_window.device_status.get("brightness", 70)
        self.brightness_stat = self._create_stat_item("💡", "亮度", f"{brightness}%")
        stats_grid.addWidget(self.brightness_stat, 1, 0)

        volume = self.main_window.device_status.get("volume", 60)
        self.volume_stat = self._create_stat_item("🔊", "音量", f"{volume}%")
        stats_grid.addWidget(self.volume_stat, 1, 1)

        layout.addLayout(stats_grid)

        layout.addStretch()

        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        wake_btn = AnimatedButton("唤醒")
        wake_btn.clicked.connect(lambda: self._send_command("wake"))
        action_layout.addWidget(wake_btn)

        sleep_btn = AnimatedButton("休眠")
        sleep_btn.setStyleSheet(get_ghost_button_style())
        sleep_btn.clicked.connect(lambda: self._send_command("sleep"))
        action_layout.addWidget(sleep_btn)

        restart_btn = AnimatedButton("重启")
        restart_btn.setStyleSheet(get_accent_button_style())
        restart_btn.clicked.connect(lambda: self._send_command("restart"))
        action_layout.addWidget(restart_btn)

        layout.addLayout(action_layout)

    def _create_stat_item(self, icon, label, value):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary']};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon_label)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(14)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {COLORS['primary_dark']};")
        layout.addWidget(value_label)

        label_text = QLabel(label)
        label_text.setAlignment(Qt.AlignCenter)
        label_text.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        layout.addWidget(label_text)

        return widget

    def _create_control_panel(self):
        self.control_card = CardWidget()
        layout = QVBoxLayout(self.control_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_label = QLabel("🎮 快捷控制")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        controls = [
            ("📖", "讲故事", "story"),
            ("🎵", "播放音乐", "music"),
            ("🔤", "英语跟读", "english"),
            ("🧮", "算术练习", "math"),
            ("🎤", "录音", "record"),
            ("📷", "拍照", "photo"),
        ]

        grid = QGridLayout()
        grid.setSpacing(12)

        for i, (icon, name, cmd) in enumerate(controls):
            btn = self._create_control_button(icon, name, cmd)
            grid.addWidget(btn, i // 3, i % 3)

        layout.addLayout(grid)

    def _create_control_button(self, icon, name, cmd):
        btn = AnimatedButton()
        btn.setFixedHeight(80)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                border-radius: 16px;
                color: {COLORS['text']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        """)

        btn_layout = QVBoxLayout(btn)
        btn_layout.setSpacing(4)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px;")
        btn_layout.addWidget(icon_label)

        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 12px; font-weight: 500;")
        btn_layout.addWidget(name_label)

        btn.clicked.connect(lambda: self._send_command(cmd))
        return btn

    def _create_device_settings_card(self):
        self.settings_card = CardWidget()
        layout = QVBoxLayout(self.settings_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_label = QLabel("⚙️ 设备设置")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        from PySide6.QtWidgets import QSlider

        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 音量")
        volume_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.main_window.device_status.get("volume", 60))
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self.volume_slider, 1)
        
        self.volume_value = QLabel(f"{self.volume_slider.value()}%")
        self.volume_value.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px; min-width: 40px;")
        volume_layout.addWidget(self.volume_value)
        layout.addLayout(volume_layout)

        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("💡 亮度")
        brightness_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        brightness_layout.addWidget(brightness_label)
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(10, 100)
        self.brightness_slider.setValue(self.main_window.device_status.get("brightness", 70))
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        brightness_layout.addWidget(self.brightness_slider, 1)
        
        self.brightness_value = QLabel(f"{self.brightness_slider.value()}%")
        self.brightness_value.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px; min-width: 40px;")
        brightness_layout.addWidget(self.brightness_value)
        layout.addLayout(brightness_layout)

        switch_layout = QGridLayout()
        switch_layout.setVerticalSpacing(16)
        switch_layout.setHorizontalSpacing(12)

        auto_sleep_label = QLabel("自动休眠")
        auto_sleep_label.setStyleSheet("font-size: 14px;")
        switch_layout.addWidget(auto_sleep_label, 0, 0)
        
        self.auto_sleep_switch = SwitchButton()
        self.auto_sleep_switch.setChecked(True)
        switch_layout.addWidget(self.auto_sleep_switch, 0, 1)

        voice_feedback_label = QLabel("语音反馈")
        voice_feedback_label.setStyleSheet("font-size: 14px;")
        switch_layout.addWidget(voice_feedback_label, 1, 0)
        
        self.voice_feedback_switch = SwitchButton()
        self.voice_feedback_switch.setChecked(True)
        switch_layout.addWidget(self.voice_feedback_switch, 1, 1)

        night_mode_label = QLabel("夜间模式")
        night_mode_label.setStyleSheet("font-size: 14px;")
        switch_layout.addWidget(night_mode_label, 2, 0)
        
        self.night_mode_switch = SwitchButton()
        self.night_mode_switch.setChecked(False)
        switch_layout.addWidget(self.night_mode_switch, 2, 1)

        switch_layout.setColumnStretch(0, 1)
        layout.addLayout(switch_layout)

        layout.addStretch()

    def _create_tasks_list_card(self):
        self.tasks_card = CardWidget()
        layout = QVBoxLayout(self.tasks_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        
        title_label = QLabel("📋 任务管理")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        add_task_btn = AnimatedButton("+ 新建任务")
        add_task_btn.setStyleSheet(get_accent_button_style())
        add_task_btn.clicked.connect(self.main_window._show_task_dialog)
        header_layout.addWidget(add_task_btn)

        layout.addLayout(header_layout)

        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setFrameShape(QFrame.NoFrame)

        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(12)
        self.tasks_scroll.setWidget(self.tasks_container)

        layout.addWidget(self.tasks_scroll, 1)

    def _on_volume_changed(self, value):
        self.volume_value.setText(f"{value}%")
        self.main_window.device_status["volume"] = value
        self.volume_stat.findChild(QLabel).setText(f"{value}%") if False else None
        for i in range(self.brightness_stat.layout().count()):
            item = self.volume_stat.layout().itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QLabel) and item.widget().text().endswith("%"):
                item.widget().setText(f"{value}%")
                break

    def _on_brightness_changed(self, value):
        self.brightness_value.setText(f"{value}%")
        self.main_window.device_status["brightness"] = value
        for i in range(self.brightness_stat.layout().count()):
            item = self.brightness_stat.layout().itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QLabel) and item.widget().text().endswith("%"):
                item.widget().setText(f"{value}%")
                break

    def _send_command(self, cmd):
        result = self.main_window.ws_client.send_control(cmd)
        msg = result.get("message", f"已发送{cmd}指令")
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "成功", msg)

    def load_data(self):
        result = self.main_window.api_client.get_tasks()
        if result.get("code") == 0:
            tasks = result.get("data", [])
            self._refresh_tasks(tasks)

        emotion = self.main_window.device_status.get("emotion", "happy")
        self.robot_face.set_emotion(emotion)

    def _refresh_tasks(self, tasks):
        while self.tasks_layout.count():
            child = self.tasks_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for task in tasks:
            item = self._create_task_row(task)
            self.tasks_layout.addWidget(item)

        if not tasks:
            empty_label = QLabel("暂无任务，点击右上角创建新任务")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px; padding: 30px;")
            self.tasks_layout.addWidget(empty_label)

        self.tasks_layout.addStretch()

    def _create_task_row(self, task):
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary']};
                border-radius: 12px;
            }}
        """)
        layout = QHBoxLayout(item)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        status = task.get("status", "pending")
        status_icon = "✅" if status == "completed" else "⏳"
        status_label = QLabel(status_icon)
        status_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(status_label)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        title_label = QLabel(task.get("title", ""))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        content_layout.addWidget(title_label)

        desc_label = QLabel(task.get("description", ""))
        desc_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        content_layout.addWidget(desc_label)

        layout.addLayout(content_layout, 1)

        reward_label = QLabel(f"🎁 {task.get('reward', '')}")
        reward_label.setStyleSheet(f"color: {COLORS['accent_dark']}; font-size: 12px; font-weight: 500;")
        layout.addWidget(reward_label)

        return item

    def update_device_status(self, status):
        emotion = status.get("emotion", "happy")
        self.robot_face.set_emotion(emotion)
        emotion_map = {
            "happy": "开心",
            "thinking": "思考中",
            "sleepy": "困倦",
            "curious": "好奇",
            "excited": "兴奋"
        }
        self.status_label.setText(f"状态: {emotion_map.get(emotion, '正常')}")

        online = status.get("online", False)
        self.online_status.setText("● 设备离线" if not online else "● 设备在线")
        self.online_status.setStyleSheet(f"""
            color: {'#7DD3A0' if online else '#FF6B6B'};
            font-size: 14px;
            font-weight: 500;
        """)

        battery = status.get("battery", self.main_window.device_status["battery"])
        for i in range(self.battery_stat.layout().count()):
            item = self.battery_stat.layout().itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QLabel) and item.widget().text().endswith("%"):
                item.widget().setText(f"{battery}%")
                break

        signal = status.get("signal", self.main_window.device_status["signal"])
        signal_text = "强" if signal >= 4 else "中" if signal >= 2 else "弱"
        for i in range(self.signal_stat.layout().count()):
            item = self.signal_stat.layout().itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QLabel) and item.widget().text() in ["强", "中", "弱"]:
                item.widget().setText(signal_text)
                break


class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("布置任务")
        self.setFixedSize(480, 520)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['secondary']};
            }}
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        title_label = QLabel("📋 布置新任务")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)

        name_label = QLabel("任务名称")
        name_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        form_layout.addWidget(name_label)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("例如：阅读绘本")
        form_layout.addWidget(self.title_input)

        desc_label = QLabel("任务描述")
        desc_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        form_layout.addWidget(desc_label)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("详细描述任务内容...")
        self.desc_input.setFixedHeight(100)
        form_layout.addWidget(self.desc_input)

        row_layout = QHBoxLayout()
        row_layout.setSpacing(12)

        reward_layout = QVBoxLayout()
        reward_label = QLabel("奖励积分")
        reward_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        reward_layout.addWidget(reward_label)

        self.reward_input = QSpinBox()
        self.reward_input.setRange(1, 100)
        self.reward_input.setValue(10)
        self.reward_input.setSuffix(" 积分")
        reward_layout.addWidget(self.reward_input)
        row_layout.addLayout(reward_layout, 1)

        type_layout = QVBoxLayout()
        type_label = QLabel("任务类型")
        type_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        type_layout.addWidget(type_label)

        self.type_input = QComboBox()
        self.type_input.addItems(["阅读", "数学", "英语", "运动", "其他"])
        type_layout.addWidget(self.type_input)
        row_layout.addLayout(type_layout, 1)

        form_layout.addLayout(row_layout)

        layout.addLayout(form_layout)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        cancel_btn = AnimatedButton("取消")
        cancel_btn.setStyleSheet(get_ghost_button_style())
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        confirm_btn = AnimatedButton("发布任务")
        confirm_btn.setStyleSheet(get_accent_button_style())
        confirm_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(confirm_btn)

        layout.addLayout(btn_layout)

    def _on_confirm(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请输入任务名称")
            return
        self.accept()

    def get_task_data(self):
        return {
            "title": self.title_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "reward": f"{self.reward_input.value()}积分",
            "due_date": int(time.time()) + 86400
        }
