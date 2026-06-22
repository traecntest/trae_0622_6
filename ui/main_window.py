from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QStackedWidget,
                               QSystemTrayIcon, QMenu, QToolBar, QDialog)
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap, QAction
from PySide6.QtCore import Qt, QTimer, QSize, Signal

from ui.widgets import AnimatedButton, PageTransitionWidget, CardWidget
from ui.styles import get_global_styles, get_accent_button_style
from config import COLORS, APP_NAME

from api.websocket_client import WebSocketClient
from api.client import APIClient


class MainWindow(QMainWindow):
    logout_signal = Signal()

    def __init__(self, db, auth_service, parent=None):
        super().__init__(parent)
        self.db = db
        self.auth_service = auth_service
        self.device_status = {
            "online": False,
            "battery": 0,
            "signal": 0,
            "emotion": "happy",
            "brightness": 70,
            "volume": 60
        }
        self.unread_count = 2
        
        self.api_client = APIClient(auth_service.current_user["token"] if auth_service.current_user else None)
        self.ws_client = WebSocketClient(self)
        self.ws_client.device_status_changed.connect(self._on_device_status_changed)
        self.ws_client.message_received.connect(self._on_message_received)
        self.ws_client.connected.connect(self._on_ws_connected)
        self.ws_client.disconnected.connect(self._on_ws_disconnected)
        
        self._setup_ui()
        self._setup_tray()
        self._connect_websocket()

    def _setup_ui(self):
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1100, 700)
        self.resize(1200, 800)
        self.setStyleSheet(get_global_styles())
        self.setWindowIcon(self._create_icon())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._create_status_bar()
        main_layout.addWidget(self.status_bar)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._create_navigation_bar()
        content_layout.addWidget(self.nav_bar)

        self._create_content_area()
        content_layout.addWidget(self.content_stack, 1)

        main_layout.addLayout(content_layout, 1)

        self._create_quick_action_bar()
        main_layout.addWidget(self.quick_action_bar)

        self._switch_page(0)

    def _create_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(COLORS["primary"]))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 60, 60)
        painter.setBrush(QColor(COLORS["text"]))
        painter.drawChord(15, 20, 12, 12, 0, 180 * 16)
        painter.drawChord(37, 20, 12, 12, 0, 180 * 16)
        painter.drawChord(22, 38, 20, 15, 0, -180 * 16)
        painter.end()
        return QIcon(pixmap)

    def _create_status_bar(self):
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(52)
        self.status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)

        layout = QHBoxLayout(self.status_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        title_label = QLabel(APP_NAME)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLORS['primary_dark']};")
        layout.addWidget(title_label)

        layout.addStretch()

        self.online_label = self._create_status_item("🔌", "离线", COLORS["error"])
        layout.addWidget(self.online_label)

        self.battery_label = self._create_status_item("🔋", "0%", COLORS["text"])
        layout.addWidget(self.battery_label)

        self.signal_label = self._create_status_item("📶", "无信号", COLORS["text"])
        layout.addWidget(self.signal_label)

        self.notification_btn = AnimatedButton()
        self.notification_btn.setFixedSize(40, 40)
        self.notification_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                border-radius: 20px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        self.notification_btn.setText("🔔")
        self.notification_btn.clicked.connect(self._show_notifications)
        layout.addWidget(self.notification_btn)

        self.unread_badge = QLabel("2")
        self.unread_badge.setParent(self.notification_btn)
        self.unread_badge.setFixedSize(18, 18)
        self.unread_badge.setAlignment(Qt.AlignCenter)
        self.unread_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['error']};
                color: white;
                border-radius: 9px;
                font-size: 11px;
                font-weight: bold;
            }}
        """)
        self.unread_badge.move(22, 2)
        self._update_unread_badge()

        user_name = self.auth_service.current_user.get("child_name", "用户") if self.auth_service.current_user else "用户"
        self.user_btn = AnimatedButton(f"👤 {user_name}")
        self.user_btn.setFixedHeight(36)
        self.user_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border-radius: 18px;
                padding: 0 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
        """)
        self.user_btn.clicked.connect(self._switch_to_profile)
        layout.addWidget(self.user_btn)

    def _create_status_item(self, icon, text, color):
        widget = QFrame()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(4)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(icon_label)

        text_label = QLabel(text)
        text_label.setObjectName("status_text")
        text_label.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 500;")
        layout.addWidget(text_label)

        widget.text_label = text_label
        return widget

    def _create_navigation_bar(self):
        self.nav_bar = QFrame()
        self.nav_bar.setFixedWidth(90)
        self.nav_bar.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(self.nav_bar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(8)

        self.nav_buttons = []
        nav_items = [
            ("🏠", "首页"),
            ("🤖", "设备"),
            ("💬", "互动"),
            ("📊", "成长"),
            ("👤", "我的")
        ]

        for i, (icon, name) in enumerate(nav_items):
            btn = self._create_nav_button(icon, name, i)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

    def _create_nav_button(self, icon, name, index):
        btn = AnimatedButton()
        btn.setFixedSize(74, 74)
        btn.setCheckable(True)
        btn.setProperty("nav_index", index)
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border-radius: 16px;
                padding: 0;
                color: {COLORS['text_light']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        """)

        btn_layout = QVBoxLayout(btn)
        btn_layout.setContentsMargins(0, 8, 0, 8)
        btn_layout.setSpacing(2)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px;")
        btn_layout.addWidget(icon_label)

        text_label = QLabel(name)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("font-size: 12px; font-weight: 500;")
        btn_layout.addWidget(text_label)

        btn.clicked.connect(lambda: self._switch_page(index))
        return btn

    def _create_content_area(self):
        self.content_stack = PageTransitionWidget()
        self.content_stack.setStyleSheet("background-color: transparent;")
        
        from ui.pages.home_page import HomePage
        from ui.pages.device_page import DevicePage
        from ui.pages.chat_page import ChatPage
        from ui.pages.growth_page import GrowthPage
        from ui.pages.profile_page import ProfilePage

        self.pages = [
            HomePage(self),
            DevicePage(self),
            ChatPage(self),
            GrowthPage(self),
            ProfilePage(self)
        ]

    def _create_quick_action_bar(self):
        self.quick_action_bar = QFrame()
        self.quick_action_bar.setFixedHeight(76)
        self.quick_action_bar.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-top: 1px solid {COLORS['border']};
            }}
        """)

        layout = QHBoxLayout(self.quick_action_bar)
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(20)

        voice_btn = AnimatedButton("🎙️ 语音通话")
        voice_btn.setFixedHeight(48)
        voice_btn.setStyleSheet(get_accent_button_style())
        voice_btn.clicked.connect(self._start_voice_call)
        layout.addWidget(voice_btn)

        emoji_btn = AnimatedButton("😊 表情包")
        emoji_btn.setFixedHeight(48)
        emoji_btn.clicked.connect(self._show_emoji_picker)
        layout.addWidget(emoji_btn)

        task_btn = AnimatedButton("📋 布置任务")
        task_btn.setFixedHeight(48)
        task_btn.clicked.connect(self._show_task_dialog)
        layout.addWidget(task_btn)

        layout.addStretch()

        status_text = "设备已连接" if self.device_status["online"] else "设备离线"
        self.quick_status = QLabel(status_text)
        self.quick_status.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px;")
        layout.addWidget(self.quick_status)

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self._create_icon())
        self.tray_icon.setToolTip(APP_NAME)

        tray_menu = QMenu()
        
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.showNormal)
        tray_menu.addAction(show_action)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _connect_websocket(self):
        self.ws_client.start()
        result = self.api_client.get_device_status()
        if result.get("code") == 0:
            self._update_device_status(result["data"])

    def _switch_page(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        page = self.pages[index]
        if not hasattr(page, "_loaded"):
            page.load_data()
            page._loaded = True
        
        if self.content_stack._current_widget is None:
            self.content_stack.set_widget(page)
        else:
            self.content_stack.transition_to(page)

    def _switch_to_profile(self):
        self._switch_page(4)

    def _on_device_status_changed(self, status):
        self._update_device_status(status)
        if hasattr(self.pages[1], "_loaded"):
            self.pages[1].update_device_status(status)

    def _update_device_status(self, status):
        self.device_status.update(status)
        
        if status.get("online"):
            self.online_label.text_label.setText("在线")
            self.online_label.text_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 13px; font-weight: 500;")
        else:
            self.online_label.text_label.setText("离线")
            self.online_label.text_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 13px; font-weight: 500;")

        battery = status.get("battery", 0)
        self.battery_label.text_label.setText(f"{battery}%")
        if battery >= 50:
            self.battery_label.text_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 13px; font-weight: 500;")
        elif battery >= 20:
            self.battery_label.text_label.setStyleSheet(f"color: {COLORS['warning']}; font-size: 13px; font-weight: 500;")
        else:
            self.battery_label.text_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 13px; font-weight: 500;")

        signal = status.get("signal", 0)
        signal_text = f"信号 {'●' * signal}{'○' * (5 - signal)}"
        self.signal_label.text_label.setText(signal_text)

        self.quick_status.setText("设备已连接" if status.get("online") else "设备离线")

    def _on_message_received(self, message):
        self.unread_count += 1
        self._update_unread_badge()
        if hasattr(self.pages[2], "_loaded"):
            self.pages[2].add_message(message)
        self.tray_icon.showMessage(
            "新消息",
            message.get("content", "收到一条新消息"),
            QSystemTrayIcon.Information,
            3000
        )

    def _update_unread_badge(self):
        if self.unread_count > 0:
            self.unread_badge.setText(str(min(self.unread_count, 99)))
            self.unread_badge.show()
        else:
            self.unread_badge.hide()

    def _on_ws_connected(self):
        self._update_device_status({"online": True})

    def _on_ws_disconnected(self):
        self._update_device_status({"online": False})

    def _start_voice_call(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "语音通话", "正在发起语音通话...")

    def _show_emoji_picker(self):
        from ui.pages.chat_page import EmojiPickerDialog
        dlg = EmojiPickerDialog(self)
        if dlg.exec() == QDialog.Accepted:
            emoji = dlg.selected_emoji
            self.ws_client.send_message(emoji, "emoji")

    def _show_task_dialog(self):
        from ui.pages.device_page import TaskDialog
        dlg = TaskDialog(self)
        if dlg.exec() == QDialog.Accepted:
            task_data = dlg.get_task_data()
            result = self.api_client.create_task(**task_data)
            if result.get("code") == 0 and hasattr(self.pages[0], "_loaded"):
                self.pages[0].load_data()
                self.pages[0].show_success_message("任务发布成功！")

    def _show_notifications(self):
        self.unread_count = 0
        self._update_unread_badge()
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "通知", "暂无新通知")

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def closeEvent(self, event):
        self.ws_client.stop()
        event.accept()
