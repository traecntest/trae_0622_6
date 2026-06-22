import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QScrollArea, QListWidget,
                               QListWidgetItem, QLineEdit, QTextEdit, QDialog,
                               QGridLayout)
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtCore import Qt, QTimer, QSize

from ui.widgets import AnimatedButton, CardWidget
from ui.styles import get_accent_button_style
from config import COLORS


class ChatPage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.messages = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self._create_conversation_list()
        layout.addWidget(self.conv_list_card, 1)

        self._create_chat_area()
        layout.addWidget(self.chat_card, 2)

    def _create_conversation_list(self):
        self.conv_list_card = CardWidget()
        layout = QVBoxLayout(self.conv_list_card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title_label = QLabel("💬 消息列表")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 搜索消息...")
        search_input.setFixedHeight(40)
        layout.addWidget(search_input)

        self.conv_list = QListWidget()
        self.conv_list.setStyleSheet(f"""
            QListWidget {{
                border: none;
                background-color: transparent;
            }}
            QListWidget::item {{
                padding: 12px;
                border-radius: 10px;
                margin: 4px 0;
                background-color: {COLORS['secondary']};
            }}
            QListWidget::item:hover {{
                background-color: #F0F7F5;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
            }}
            QListWidget::item:selected * {{
                color: white;
            }}
        """)
        self.conv_list.itemClicked.connect(self._on_conversation_selected)
        layout.addWidget(self.conv_list, 1)

    def _create_chat_area(self):
        self.chat_card = CardWidget()
        layout = QVBoxLayout(self.chat_card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.chat_header = QFrame()
        self.chat_header.setFixedHeight(70)
        self.chat_header.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-bottom: 1px solid {COLORS['border']};
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }}
        """)
        header_layout = QHBoxLayout(self.chat_header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        avatar_label = QLabel("👦")
        avatar_label.setFixedSize(44, 44)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['secondary']};
                border-radius: 22px;
                font-size: 22px;
            }}
        """)
        header_layout.addWidget(avatar_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        child_name = self.main_window.auth_service.current_user.get("child_name", "宝贝") if self.main_window.auth_service.current_user else "宝贝"
        name_label = QLabel(child_name)
        name_font = QFont()
        name_font.setPointSize(15)
        name_font.setBold(True)
        name_label.setFont(name_font)
        info_layout.addWidget(name_label)

        self.online_label = QLabel("● 在线")
        self.online_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 12px;")
        info_layout.addWidget(self.online_label)

        header_layout.addLayout(info_layout)
        header_layout.addStretch()

        call_btn = AnimatedButton("📞")
        call_btn.setFixedSize(40, 40)
        call_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                border-radius: 20px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        call_btn.clicked.connect(self.main_window._start_voice_call)
        header_layout.addWidget(call_btn)

        layout.addWidget(self.chat_header)

        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setFrameShape(QFrame.NoFrame)
        self.messages_scroll.setStyleSheet("background-color: #FAFAFA;")

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(16)
        self.messages_scroll.setWidget(self.messages_container)

        layout.addWidget(self.messages_scroll, 1)

        self.input_area = QFrame()
        self.input_area.setFixedHeight(80)
        self.input_area.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-top: 1px solid {COLORS['border']};
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
            }}
        """)
        input_layout = QHBoxLayout(self.input_area)
        input_layout.setContentsMargins(16, 16, 16, 16)
        input_layout.setSpacing(10)

        emoji_btn = AnimatedButton("😊")
        emoji_btn.setFixedSize(44, 44)
        emoji_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                border-radius: 22px;
                font-size: 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        emoji_btn.clicked.connect(self._show_emoji_picker)
        input_layout.addWidget(emoji_btn)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("输入消息...")
        self.message_input.setFixedHeight(48)
        self.message_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 24px;
                padding: 12px 16px;
                font-size: 14px;
            }}
            QTextEdit:focus {{
                border-color: {COLORS['primary']};
            }}
        """)
        input_layout.addWidget(self.message_input, 1)

        voice_btn = AnimatedButton("🎤")
        voice_btn.setFixedSize(44, 44)
        voice_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                border-radius: 22px;
                font-size: 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        voice_btn.clicked.connect(self._record_voice)
        input_layout.addWidget(voice_btn)

        send_btn = AnimatedButton("发送")
        send_btn.setFixedSize(70, 44)
        send_btn.setStyleSheet(get_accent_button_style())
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(send_btn)

        layout.addWidget(self.input_area)

    def _on_conversation_selected(self, item):
        pass

    def _show_emoji_picker(self):
        dlg = EmojiPickerDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.message_input.insertPlainText(dlg.selected_emoji)

    def _record_voice(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "语音消息", "正在录音，再次点击结束...")

    def _send_message(self):
        content = self.message_input.toPlainText().strip()
        if not content:
            return

        message = {
            "id": int(time.time()),
            "sender": "parent",
            "content": content,
            "msg_type": "text",
            "timestamp": int(time.time())
        }
        
        self.main_window.ws_client.send_message(content)
        self.add_message(message)
        self.message_input.clear()

        QTimer.singleShot(1500, self._mock_reply)

    def _mock_reply(self):
        replies = [
            "好的妈妈！😊",
            "我知道啦~",
            "好嘞！",
            "收到！👍",
            "嗯嗯，我会的！"
        ]
        import random
        reply = {
            "id": int(time.time()),
            "sender": "child",
            "content": random.choice(replies),
            "msg_type": "text",
            "timestamp": int(time.time())
        }
        self.add_message(reply)

    def add_message(self, message):
        self.messages.append(message)
        self._add_message_bubble(message)
        self._refresh_conversation_list()
        
        QTimer.singleShot(100, self._scroll_to_bottom)

    def _add_message_bubble(self, message):
        sender = message.get("sender", "child")
        content = message.get("content", "")
        msg_type = message.get("msg_type", "text")
        timestamp = message.get("timestamp", int(time.time()))

        bubble_wrapper = QWidget()
        wrapper_layout = QHBoxLayout(bubble_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        if sender == "parent":
            wrapper_layout.addStretch()

        if sender != "parent":
            avatar_label = QLabel("👦" if sender == "child" else "🤖")
            avatar_label.setFixedSize(36, 36)
            avatar_label.setAlignment(Qt.AlignCenter)
            avatar_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['primary']};
                    border-radius: 18px;
                    font-size: 16px;
                    color: white;
                }}
            """)
            wrapper_layout.addWidget(avatar_label)
            wrapper_layout.addSpacing(8)

        bubble = QFrame()
        bubble.setMaximumWidth(400)
        bubble.setStyleSheet(f"""
            QFrame {{
                background-color: {'#8ED7C4' if sender == 'parent' else 'white'};
                border-radius: 16px;
                padding: 12px 16px;
            }}
        """)

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.setSpacing(4)

        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f"""
            color: {'white' if sender == 'parent' else COLORS['text']};
            font-size: 14px;
        """)
        if msg_type == "voice":
            content_label.setText("🎤 " + content)
        elif msg_type == "system":
            content_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px;")
            bubble.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['secondary']};
                    border-radius: 16px;
                    padding: 12px 16px;
                }}
            """)
        bubble_layout.addWidget(content_label)

        time_str = time.strftime("%H:%M", time.localtime(timestamp))
        time_label = QLabel(time_str)
        time_label.setAlignment(Qt.AlignRight if sender == "parent" else Qt.AlignLeft)
        time_label.setStyleSheet(f"""
            color: {'rgba(255,255,255,0.7)' if sender == 'parent' else COLORS['text_light']};
            font-size: 11px;
        """)
        bubble_layout.addWidget(time_label)

        wrapper_layout.addWidget(bubble)

        if sender == "parent":
            wrapper_layout.addSpacing(8)
            avatar_label = QLabel("👩")
            avatar_label.setFixedSize(36, 36)
            avatar_label.setAlignment(Qt.AlignCenter)
            avatar_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['accent']};
                    border-radius: 18px;
                    font-size: 16px;
                    color: white;
                }}
            """)
            wrapper_layout.addWidget(avatar_label)
        else:
            wrapper_layout.addStretch()

        self.messages_layout.addWidget(bubble_wrapper)

    def _scroll_to_bottom(self):
        scrollbar = self.messages_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _refresh_conversation_list(self):
        self.conv_list.clear()
        
        conversations = [
            ("👦", "宝贝", "今天有什么有趣的事吗？", "刚刚", 2),
            ("🤖", "可伴助手", "孩子完成了数学练习", "5分钟前", 1),
            ("📢", "系统通知", "您订阅的内容已更新", "昨天", 0)
        ]

        for icon, name, last_msg, time_str, unread in conversations:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 70))

            widget = QFrame()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(10)

            avatar_label = QLabel(icon)
            avatar_label.setFixedSize(44, 44)
            avatar_label.setAlignment(Qt.AlignCenter)
            avatar_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['secondary']};
                    border-radius: 22px;
                    font-size: 20px;
                }}
            """)
            layout.addWidget(avatar_label)

            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)

            name_layout = QHBoxLayout()
            name_label = QLabel(name)
            name_font = QFont()
            name_font.setBold(True)
            name_label.setFont(name_font)
            name_layout.addWidget(name_label)
            name_layout.addStretch()
            
            time_label = QLabel(time_str)
            time_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 11px;")
            name_layout.addWidget(time_label)

            info_layout.addLayout(name_layout)

            msg_layout = QHBoxLayout()
            last_msg_label = QLabel(last_msg)
            last_msg_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
            last_msg_label.setMaximumWidth(160)
            last_msg_label.setTextInteractionFlags(Qt.NoTextInteraction)
            msg_layout.addWidget(last_msg_label)
            msg_layout.addStretch()

            if unread > 0:
                unread_label = QLabel(str(unread))
                unread_label.setFixedSize(18, 18)
                unread_label.setAlignment(Qt.AlignCenter)
                unread_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {COLORS['error']};
                        color: white;
                        border-radius: 9px;
                        font-size: 11px;
                        font-weight: bold;
                    }}
                """)
                msg_layout.addWidget(unread_label)

            info_layout.addLayout(msg_layout)

            layout.addLayout(info_layout, 1)

            self.conv_list.addItem(item)
            self.conv_list.setItemWidget(item, widget)

        if self.conv_list.count() > 0:
            self.conv_list.setCurrentRow(0)

    def load_data(self):
        result = self.main_window.api_client.get_messages()
        if result.get("code") == 0:
            self.messages = result.get("data", [])
            
            while self.messages_layout.count():
                child = self.messages_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            for msg in self.messages:
                self._add_message_bubble(msg)
            
            self._refresh_conversation_list()
            QTimer.singleShot(100, self._scroll_to_bottom)


class EmojiPickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_emoji = None
        self.setWindowTitle("选择表情")
        self.setFixedSize(360, 320)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: white;
                border-radius: 16px;
            }}
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title_label = QLabel("😊 选择表情")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        emojis = [
            "😊", "😂", "🥰", "😘", "🤗", "😋", "🤔", "😴",
            "👍", "👏", "🙌", "🤝", "💪", "❤️", "💖", "💕",
            "🎉", "🎊", "✨", "🌟", "⭐", "🌈", "☀️", "🌙",
            "📚", "🎨", "🎵", "🎮", "🧸", "🍭", "🍎", "🏆"
        ]

        grid = QGridLayout()
        grid.setSpacing(8)

        for i, emoji in enumerate(emojis):
            btn = AnimatedButton(emoji)
            btn.setFixedSize(50, 50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['secondary']};
                    border-radius: 25px;
                    font-size: 24px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['primary']};
                }}
            """)
            btn.clicked.connect(lambda e, em=emoji: self._on_emoji_selected(em))
            grid.addWidget(btn, i // 8, i % 8)

        layout.addLayout(grid, 1)

        btn_layout = QHBoxLayout()
        cancel_btn = AnimatedButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _on_emoji_selected(self, emoji):
        self.selected_emoji = emoji
        self.accept()
