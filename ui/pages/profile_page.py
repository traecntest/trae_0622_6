import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QScrollArea, QSlider,
                               QComboBox, QMessageBox, QDialog)
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtCore import Qt, QTimer, QSize

from ui.widgets import AnimatedButton, CardWidget, SwitchButton
from ui.styles import get_accent_button_style, get_ghost_button_style
from config import COLORS, APP_NAME, APP_VERSION


class ProfilePage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        self._create_profile_card()
        left_layout.addWidget(self.profile_card)

        self._create_settings_card()
        left_layout.addWidget(self.settings_card, 1)

        layout.addLayout(left_layout, 1)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)

        self._create_notification_card()
        right_layout.addWidget(self.notification_card)

        self._create_about_card()
        right_layout.addWidget(self.about_card)

        self._create_danger_zone_card()
        right_layout.addWidget(self.danger_zone_card)

        layout.addLayout(right_layout, 1)

    def _create_profile_card(self):
        self.profile_card = CardWidget()
        self.profile_card.setFixedHeight(160)
        layout = QHBoxLayout(self.profile_card)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(20)

        avatar_label = QLabel("👩")
        avatar_label.setFixedSize(100, 100)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['primary']};
                border-radius: 50px;
                font-size: 48px;
                color: white;
            }}
        """)
        layout.addWidget(avatar_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        name_label = QLabel("家长用户")
        name_font = QFont()
        name_font.setPointSize(22)
        name_font.setBold(True)
        name_label.setFont(name_font)
        info_layout.addWidget(name_label)

        phone = self.main_window.auth_service.current_user.get("phone", "") if self.main_window.auth_service.current_user else ""
        phone_label = QLabel(f"📱 {phone[:3]}****{phone[-4:]}")
        phone_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
        info_layout.addWidget(phone_label)

        child_name = self.main_window.auth_service.current_user.get("child_name", "未绑定") if self.main_window.auth_service.current_user else "未绑定"
        child_age = self.main_window.auth_service.current_user.get("child_age", 0) if self.main_window.auth_service.current_user else 0
        child_label = QLabel(f"👦 {child_name}" + (f" · {child_age}岁" if child_age > 0 else ""))
        child_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
        info_layout.addWidget(child_label)

        device_serial = self.main_window.auth_service.current_user.get("device_serial", "未绑定") if self.main_window.auth_service.current_user else "未绑定"
        device_label = QLabel(f"🤖 设备: {device_serial}")
        device_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
        info_layout.addWidget(device_label)

        info_layout.addStretch()
        layout.addLayout(info_layout, 1)

        edit_btn = AnimatedButton("✏️ 编辑资料")
        edit_btn.setStyleSheet(get_ghost_button_style())
        edit_btn.clicked.connect(self._edit_profile)
        layout.addWidget(edit_btn)

    def _create_settings_card(self):
        self.settings_card = CardWidget()
        layout = QVBoxLayout(self.settings_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_label = QLabel("⚙️ 系统设置")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 提醒音量")
        volume_label.setStyleSheet("font-size: 14px;")
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(200)
        volume_layout.addWidget(self.volume_slider, 1)
        
        self.volume_value = QLabel(f"{self.volume_slider.value()}%")
        self.volume_value.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px; min-width: 40px;")
        volume_layout.addWidget(self.volume_value)
        self.volume_slider.valueChanged.connect(lambda v: self.volume_value.setText(f"{v}%"))
        layout.addLayout(volume_layout)

        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("💡 界面亮度")
        brightness_label.setStyleSheet("font-size: 14px;")
        brightness_layout.addWidget(brightness_label)
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(30, 100)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setFixedWidth(200)
        brightness_layout.addWidget(self.brightness_slider, 1)
        
        self.brightness_value = QLabel(f"{self.brightness_slider.value()}%")
        self.brightness_value.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px; min-width: 40px;")
        brightness_layout.addWidget(self.brightness_value)
        self.brightness_slider.valueChanged.connect(lambda v: self.brightness_value.setText(f"{v}%"))
        layout.addLayout(brightness_layout)

        theme_layout = QHBoxLayout()
        theme_label = QLabel("🎨 界面主题")
        theme_label.setStyleSheet("font-size: 14px;")
        theme_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["温暖治愈（推荐）", "清新薄荷", "明亮活力", "深色模式"])
        self.theme_combo.setFixedWidth(200)
        self.theme_combo.currentIndexChanged.connect(self._change_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        language_layout = QHBoxLayout()
        language_label = QLabel("🌐 语言设置")
        language_label.setStyleSheet("font-size: 14px;")
        language_layout.addWidget(language_label)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "繁體中文", "English"])
        self.language_combo.setFixedWidth(200)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        layout.addLayout(language_layout)

        settings = [
            ("🔔 消息通知", True),
            ("🔊 声音提醒", True),
            ("📳 振动反馈", False),
            ("🌙 勿扰模式", False),
            ("☁️ 自动同步", True)
        ]

        for label, default in settings:
            setting_row = self._create_setting_row(label, default)
            layout.addWidget(setting_row)

        layout.addStretch()

    def _create_setting_row(self, label, default):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary']};
                border-radius: 12px;
                padding: 12px 16px;
            }}
        """)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-size: 14px;")
        layout.addWidget(label_widget)

        layout.addStretch()

        switch = SwitchButton()
        switch.setChecked(default)
        switch.toggled.connect(lambda checked, lbl=label: self._on_setting_changed(lbl, checked))
        layout.addWidget(switch)

        return widget

    def _create_notification_card(self):
        self.notification_card = CardWidget()
        layout = QVBoxLayout(self.notification_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_label = QLabel("🔔 通知管理")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        notif_types = [
            ("任务完成提醒", True),
            ("设备离线提醒", True),
            ("孩子互动提醒", True),
            ("每日成长报告", True),
            ("内容更新提醒", False)
        ]

        for label, default in notif_types:
            row = self._create_notif_row(label, default)
            layout.addWidget(row)

        layout.addStretch()

    def _create_notif_row(self, label, default):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary']};
                border-radius: 12px;
                padding: 10px 14px;
            }}
        """)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-size: 13px;")
        layout.addWidget(label_widget)

        layout.addStretch()

        switch = SwitchButton()
        switch.setChecked(default)
        layout.addWidget(switch)

        return widget

    def _create_about_card(self):
        self.about_card = CardWidget()
        layout = QVBoxLayout(self.about_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("ℹ️ 关于可伴")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        info_layout = QGridLayout()
        info_layout.setVerticalSpacing(8)
        info_layout.setHorizontalSpacing(12)

        info_items = [
            ("应用名称", APP_NAME),
            ("应用版本", f"v{APP_VERSION}"),
            ("设备型号", "可伴智能陪伴机器人"),
            ("服务热线", "400-888-8888"),
            ("官方邮箱", "support@keban.com"),
            ("用户协议", "点击查看"),
            ("隐私政策", "点击查看")
        ]

        for i, (key, value) in enumerate(info_items):
            key_label = QLabel(key)
            key_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px;")
            info_layout.addWidget(key_label, i, 0)

            value_label = QLabel(value)
            value_label.setStyleSheet(f"font-size: 13px;")
            if key in ["用户协议", "隐私政策"]:
                value_label.setStyleSheet(f"color: {COLORS['primary_dark']}; font-size: 13px; text-decoration: underline;")
                value_label.setCursor(Qt.PointingHandCursor)
            info_layout.addWidget(value_label, i, 1)

        layout.addLayout(info_layout)

        btn_layout = QHBoxLayout()
        check_update_btn = AnimatedButton("检查更新")
        check_update_btn.setStyleSheet(get_ghost_button_style())
        check_update_btn.clicked.connect(self._check_update)
        btn_layout.addWidget(check_update_btn)

        feedback_btn = AnimatedButton("意见反馈")
        feedback_btn.setStyleSheet(get_ghost_button_style())
        feedback_btn.clicked.connect(self._send_feedback)
        btn_layout.addWidget(feedback_btn)

        layout.addLayout(btn_layout)

    def _create_danger_zone_card(self):
        self.danger_zone_card = CardWidget()
        layout = QVBoxLayout(self.danger_zone_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_label = QLabel("⚠️ 账号管理")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        hint_label = QLabel("以下操作不可逆，请谨慎操作")
        hint_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        layout.addWidget(hint_label)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        clear_cache_btn = AnimatedButton("🗑️ 清除缓存")
        clear_cache_btn.setStyleSheet(get_ghost_button_style())
        clear_cache_btn.clicked.connect(self._clear_cache)
        btn_layout.addWidget(clear_cache_btn)

        switch_account_btn = AnimatedButton("🔄 切换账号")
        switch_account_btn.setStyleSheet(get_ghost_button_style())
        switch_account_btn.clicked.connect(self._switch_account)
        btn_layout.addWidget(switch_account_btn)

        logout_btn = AnimatedButton("🚪 退出登录")
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #FF5252;
            }}
        """)
        logout_btn.clicked.connect(self._logout)
        btn_layout.addWidget(logout_btn)

        layout.addLayout(btn_layout)

    def _edit_profile(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "提示", "编辑资料功能开发中...")

    def _change_theme(self, index):
        themes = ["温暖治愈", "清新薄荷", "明亮活力", "深色模式"]
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "主题切换", f"已切换到「{themes[index]}」主题")

    def _on_setting_changed(self, label, checked):
        status = "开启" if checked else "关闭"
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "设置", f"{label}已{status}")

    def _check_update(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "检查更新", "当前已是最新版本！")

    def _send_feedback(self):
        from PySide6.QtWidgets import QMessageBox, QTextEdit, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle("意见反馈")
        dlg.setFixedSize(400, 300)
        dlg.setStyleSheet(f"background-color: {COLORS['secondary']};")
        
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("📝 请描述您的问题或建议")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        text_edit = QTextEdit()
        text_edit.setPlaceholderText("感谢您的反馈，我们会认真对待每一条建议...")
        layout.addWidget(text_edit, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("提交")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        if dlg.exec() == QDialog.Accepted:
            if text_edit.toPlainText().strip():
                QMessageBox.information(self, "提交成功", "感谢您的反馈！我们会尽快处理。")

    def _clear_cache(self):
        reply = QMessageBox.question(
            self, "确认清除",
            "确定要清除本地缓存吗？这将删除所有临时数据。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "成功", "缓存已清除！")

    def _switch_account(self):
        reply = QMessageBox.question(
            self, "确认切换",
            "确定要切换账号吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._do_logout()

    def _logout(self):
        reply = QMessageBox.question(
            self, "确认退出",
            "确定要退出登录吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._do_logout()

    def _do_logout(self):
        self.main_window.auth_service.logout()
        self.main_window.ws_client.disconnect()
        
        from ui.login_page import LoginPage
        self.login_page = LoginPage(self.main_window.db, self.main_window.auth_service)
        self.login_page.show()
        self.main_window.close()

    def load_data(self):
        pass
