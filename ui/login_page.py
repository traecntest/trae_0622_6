import re
import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFrame, QSpinBox,
                               QMessageBox, QGraphicsDropShadowEffect)
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal

from ui.widgets import AnimatedButton, CardWidget, RobotFaceWidget
from ui.styles import get_global_styles, get_error_input_style, get_accent_button_style
from config import COLORS, TEST_VERIFICATION_CODE, TEST_DEVICE_SERIAL


class LoginPage(QWidget):
    login_success = Signal()

    def __init__(self, db, auth_service, parent=None):
        super().__init__(parent)
        self.db = db
        self.auth_service = auth_service
        self.countdown_timer = QTimer(self)
        self.countdown_time = 60
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("可伴桌面 - 登录")
        self.setMinimumSize(480, 640)
        self.setStyleSheet(get_global_styles())
        self.setWindowIcon(self._create_icon())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack_widget = QFrame(self)
        self.stack_layout = QVBoxLayout(self.stack_widget)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack_widget)

        self._show_login_form()

    def _create_icon(self):
        from PySide6.QtGui import QPixmap, QPainter
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

    def _show_login_form(self):
        self._clear_stack()

        card = CardWidget()
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        robot_widget = RobotFaceWidget()
        robot_widget.setFixedSize(120, 120)
        robot_widget.set_emotion("happy")
        header_layout.addWidget(robot_widget, 0, Qt.AlignCenter)

        title_label = QLabel("欢迎使用可伴")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        subtitle_label = QLabel("陪伴孩子快乐成长")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
        header_layout.addWidget(subtitle_label)

        card_layout.addLayout(header_layout)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)

        phone_label = QLabel("手机号")
        phone_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        form_layout.addWidget(phone_label)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("请输入手机号")
        self.phone_input.setMaxLength(11)
        self.phone_input.textChanged.connect(self._on_phone_changed)
        self.phone_input.returnPressed.connect(self._on_code_input_return)
        form_layout.addWidget(self.phone_input)

        self.phone_error = QLabel("")
        self.phone_error.setStyleSheet(f"color: {COLORS['error']}; font-size: 12px;")
        self.phone_error.setVisible(False)
        form_layout.addWidget(self.phone_error)

        code_layout = QVBoxLayout()
        code_label = QLabel("验证码")
        code_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        code_layout.addWidget(code_label)

        code_input_layout = QHBoxLayout()
        code_input_layout.setSpacing(10)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("请输入验证码")
        self.code_input.setMaxLength(6)
        self.code_input.returnPressed.connect(self._on_login_clicked)
        code_input_layout.addWidget(self.code_input, 1)

        self.send_code_btn = AnimatedButton("获取验证码")
        self.send_code_btn.setFixedWidth(120)
        self.send_code_btn.setStyleSheet(get_accent_button_style())
        self.send_code_btn.clicked.connect(self._on_send_code_clicked)
        self.send_code_btn.setEnabled(False)
        code_input_layout.addWidget(self.send_code_btn)

        code_layout.addLayout(code_input_layout)

        self.code_error = QLabel("")
        self.code_error.setStyleSheet(f"color: {COLORS['error']}; font-size: 12px;")
        self.code_error.setVisible(False)
        code_layout.addWidget(self.code_error)

        form_layout.addLayout(code_layout)

        tip_label = QLabel(f"测试验证码: {TEST_VERIFICATION_CODE}")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        form_layout.addWidget(tip_label)

        card_layout.addLayout(form_layout)

        self.login_btn = AnimatedButton("登 录")
        self.login_btn.setFixedHeight(48)
        login_font = QFont()
        login_font.setPointSize(16)
        login_font.setBold(True)
        self.login_btn.setFont(login_font)
        self.login_btn.clicked.connect(self._on_login_clicked)
        self.login_btn.setEnabled(False)
        card_layout.addWidget(self.login_btn)

        agreement_label = QLabel("登录即表示同意《用户协议》和《隐私政策》")
        agreement_label.setAlignment(Qt.AlignCenter)
        agreement_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        card_layout.addWidget(agreement_label)

        center_layout = QVBoxLayout(self.stack_layout.widget())
        center_layout = QVBoxLayout()
        center_layout.addWidget(card, 0, Qt.AlignCenter)
        self.stack_layout.addLayout(center_layout)

    def _clear_stack(self):
        while self.stack_layout.count():
            child = self.stack_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

    def _validate_phone(self, phone):
        if not phone:
            return False, "请输入手机号"
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return False, "请输入正确的手机号格式"
        return True, ""

    def _validate_code(self, code):
        if not code:
            return False, "请输入验证码"
        if len(code) != 6:
            return False, "验证码为6位数字"
        if not code.isdigit():
            return False, "验证码只能是数字"
        return True, ""

    def _on_phone_changed(self, text):
        valid, msg = self._validate_phone(text)
        self.phone_error.setText(msg)
        self.phone_error.setVisible(not valid and len(text) > 0)
        
        if not valid and len(text) > 0:
            self.phone_input.setStyleSheet(get_error_input_style())
        else:
            self.phone_input.setStyleSheet("")
        
        self.send_code_btn.setEnabled(valid)
        self._update_login_btn()

    def _on_code_input_return(self):
        if self.send_code_btn.isEnabled():
            self._on_send_code_clicked()

    def _on_send_code_clicked(self):
        phone = self.phone_input.text().strip()
        valid, msg = self._validate_phone(phone)
        
        if not valid:
            self.phone_error.setText(msg)
            self.phone_error.setVisible(True)
            self.phone_input.setStyleSheet(get_error_input_style())
            return

        result = self.auth_service.send_verification_code(phone)
        if result.get("code") == 0:
            self._start_countdown()
        else:
            QMessageBox.warning(self, "提示", result.get("message", "发送失败"))

    def _start_countdown(self):
        self.countdown_time = 60
        self.send_code_btn.setEnabled(False)
        self.countdown_timer.timeout.connect(self._update_countdown)
        self.countdown_timer.start(1000)
        self._update_countdown()

    def _update_countdown(self):
        if self.countdown_time > 0:
            self.send_code_btn.setText(f"{self.countdown_time}s")
            self.countdown_time -= 1
        else:
            self.countdown_timer.stop()
            self.countdown_timer.timeout.disconnect()
            self.send_code_btn.setText("重新获取")
            self.send_code_btn.setEnabled(True)

    def _update_login_btn(self):
        phone = self.phone_input.text().strip()
        code = self.code_input.text().strip()
        phone_valid, _ = self._validate_phone(phone)
        code_valid = len(code) == 6 and code.isdigit()
        self.login_btn.setEnabled(phone_valid and code_valid)

    def _on_login_clicked(self):
        phone = self.phone_input.text().strip()
        code = self.code_input.text().strip()

        phone_valid, phone_msg = self._validate_phone(phone)
        if not phone_valid:
            self.phone_error.setText(phone_msg)
            self.phone_error.setVisible(True)
            self.phone_input.setStyleSheet(get_error_input_style())
            self._shake_widget(self.phone_input)
            return

        code_valid, code_msg = self._validate_code(code)
        if not code_valid:
            self.code_error.setText(code_msg)
            self.code_error.setVisible(True)
            self.code_input.setStyleSheet(get_error_input_style())
            self._shake_widget(self.code_input)
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("登录中...")

        QTimer.singleShot(500, lambda: self._do_login(phone, code))

    def _do_login(self, phone, code):
        result = self.auth_service.login(phone, code)
        
        if result.get("code") == 0:
            if self.auth_service.is_child_binded():
                self.login_success.emit()
                self.close()
            else:
                self._show_bind_form()
        else:
            self.code_error.setText(result.get("message", "登录失败"))
            self.code_error.setVisible(True)
            self.code_input.setStyleSheet(get_error_input_style())
            self._shake_widget(self.code_input)
            self.login_btn.setEnabled(True)
            self.login_btn.setText("登 录")

    def _shake_widget(self, widget):
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(500)
        original_pos = widget.pos()
        animation.setKeyValueAt(0, original_pos)
        animation.setKeyValueAt(0.1, original_pos + widget.pos().__class__(-5, 0))
        animation.setKeyValueAt(0.2, original_pos + widget.pos().__class__(5, 0))
        animation.setKeyValueAt(0.3, original_pos + widget.pos().__class__(-5, 0))
        animation.setKeyValueAt(0.4, original_pos + widget.pos().__class__(5, 0))
        animation.setKeyValueAt(0.5, original_pos + widget.pos().__class__(-5, 0))
        animation.setKeyValueAt(0.6, original_pos + widget.pos().__class__(5, 0))
        animation.setKeyValueAt(0.7, original_pos + widget.pos().__class__(-3, 0))
        animation.setKeyValueAt(0.8, original_pos + widget.pos().__class__(3, 0))
        animation.setKeyValueAt(0.9, original_pos + widget.pos().__class__(-1, 0))
        animation.setKeyValueAt(1, original_pos)
        animation.setEasingCurve(QEasingCurve.Linear)
        animation.start()

    def _show_bind_form(self):
        self._clear_stack()

        card = CardWidget()
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        title_label = QLabel("绑定孩子信息")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        card_layout.addWidget(title_label)

        subtitle_label = QLabel("首次使用请绑定孩子信息与设备")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
        card_layout.addWidget(subtitle_label)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)

        name_label = QLabel("孩子姓名")
        name_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        form_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入孩子姓名")
        self.name_input.textChanged.connect(self._update_bind_btn)
        self.name_input.returnPressed.connect(self._on_bind_clicked)
        form_layout.addWidget(self.name_input)

        age_label = QLabel("孩子年龄")
        age_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        form_layout.addWidget(age_label)

        self.age_input = QSpinBox()
        self.age_input.setRange(1, 18)
        self.age_input.setValue(5)
        self.age_input.setSuffix(" 岁")
        form_layout.addWidget(self.age_input)

        serial_label = QLabel("设备序列号")
        serial_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        form_layout.addWidget(serial_label)

        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("请输入机器人序列号")
        self.serial_input.setText(TEST_DEVICE_SERIAL)
        self.serial_input.textChanged.connect(self._update_bind_btn)
        self.serial_input.returnPressed.connect(self._on_bind_clicked)
        form_layout.addWidget(self.serial_input)

        tip_label = QLabel(f"测试设备号已自动填充: {TEST_DEVICE_SERIAL}")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        form_layout.addWidget(tip_label)

        card_layout.addLayout(form_layout)

        self.bind_btn = AnimatedButton("完成绑定")
        self.bind_btn.setFixedHeight(48)
        bind_font = QFont()
        bind_font.setPointSize(16)
        bind_font.setBold(True)
        self.bind_btn.setFont(bind_font)
        self.bind_btn.clicked.connect(self._on_bind_clicked)
        card_layout.addWidget(self.bind_btn)

        skip_btn = QPushButton("稍后绑定")
        skip_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_light']};
                border: none;
                padding: 8px;
            }}
            QPushButton:hover {{
                color: {COLORS['primary_dark']};
            }}
        """)
        skip_btn.clicked.connect(self._on_skip_bind)
        card_layout.addWidget(skip_btn)

        center_layout = QVBoxLayout()
        center_layout.addWidget(card, 0, Qt.AlignCenter)
        self.stack_layout.addLayout(center_layout)

    def _update_bind_btn(self):
        name = self.name_input.text().strip()
        serial = self.serial_input.text().strip()
        self.bind_btn.setEnabled(bool(name) and bool(serial))

    def _on_bind_clicked(self):
        name = self.name_input.text().strip()
        age = self.age_input.value()
        serial = self.serial_input.text().strip()

        if not name:
            QMessageBox.warning(self, "提示", "请输入孩子姓名")
            return
        if not serial:
            QMessageBox.warning(self, "提示", "请输入设备序列号")
            return

        self.bind_btn.setEnabled(False)
        self.bind_btn.setText("绑定中...")

        QTimer.singleShot(500, lambda: self._do_bind(name, age, serial))

    def _do_bind(self, name, age, serial):
        result = self.auth_service.bind_child(name, age, serial)
        if result.get("code") == 0:
            self.login_success.emit()
            self.close()
        else:
            QMessageBox.warning(self, "提示", result.get("message", "绑定失败"))
            self.bind_btn.setEnabled(True)
            self.bind_btn.setText("完成绑定")

    def _on_skip_bind(self):
        reply = QMessageBox.question(
            self, "确认",
            "跳过绑定将无法使用设备控制功能，确定要跳过吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.login_success.emit()
            self.close()
