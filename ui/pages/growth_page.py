import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QScrollArea, QTabWidget,
                               QGridLayout, QListWidget, QListWidgetItem,
                               QGraphicsView, QGraphicsScene)
from PySide6.QtGui import (QColor, QFont, QPainter, QPen, QBrush, 
                          QLinearGradient, QPainterPath, QIcon)
from PySide6.QtCore import Qt, QTimer, QSize, QRectF

from ui.widgets import AnimatedButton, CardWidget, SwitchButton
from ui.styles import get_accent_button_style, get_ghost_button_style
from config import COLORS


class GrowthPage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.records = []
        self.subscriptions = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self._create_summary_card()
        layout.addWidget(self.summary_card)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: transparent;
            }}
            QTabBar::tab {{
                background-color: transparent;
                padding: 12px 28px;
                font-size: 15px;
                font-weight: 500;
                color: {COLORS['text_light']};
                border-bottom: 3px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {COLORS['primary_dark']};
                border-bottom-color: {COLORS['primary']};
            }}
        """)

        self._create_timeline_tab()
        self._create_subscription_tab()

        self.tab_widget.addTab(self.timeline_tab, "📊 成长档案")
        self.tab_widget.addTab(self.subscription_tab, "📚 内容订阅")
        layout.addWidget(self.tab_widget, 1)

    def _create_summary_card(self):
        self.summary_card = CardWidget()
        self.summary_card.setFixedHeight(120)
        layout = QHBoxLayout(self.summary_card)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(20)

        greeting_layout = QVBoxLayout()
        greeting_layout.setSpacing(4)

        child_name = self.main_window.auth_service.current_user.get("child_name", "宝贝") if self.main_window.auth_service.current_user else "宝贝"
        title_label = QLabel(f"{child_name}的成长档案")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        greeting_layout.addWidget(title_label)

        subtitle_label = QLabel("记录每一个成长瞬间 🌟")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
        greeting_layout.addWidget(subtitle_label)

        layout.addLayout(greeting_layout)
        layout.addStretch()

        stats = [
            ("📝", "互动记录", "32"),
            ("✅", "完成任务", "18"),
            ("😊", "平均心情", "4.8"),
            ("🔥", "连续记录", "7天")
        ]
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

    def _create_timeline_tab(self):
        self.timeline_tab = QWidget()
        layout = QHBoxLayout(self.timeline_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        self.mood_card = self._create_mood_chart_card()
        left_layout.addWidget(self.mood_card)

        self.timeline_card = self._create_timeline_card()
        left_layout.addWidget(self.timeline_card, 1)

        layout.addLayout(left_layout, 2)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)

        self.achievement_card = self._create_achievement_card()
        right_layout.addWidget(self.achievement_card)

        self.stats_card = self._create_stats_card()
        right_layout.addWidget(self.stats_card, 1)

        layout.addLayout(right_layout, 1)

    def _create_mood_chart_card(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("📈 情绪变化曲线")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        self.mood_chart = MoodChartWidget()
        self.mood_chart.setFixedHeight(140)
        layout.addWidget(self.mood_chart)

        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(20)
        
        moods = ["😊 开心", "😐 一般", "😢 低落"]
        for mood in moods:
            lbl = QLabel(mood)
            lbl.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
            legend_layout.addWidget(lbl)
        legend_layout.addStretch()
        
        avg_lbl = QLabel("近7天平均: 4.8 😊")
        avg_lbl.setStyleSheet(f"color: {COLORS['primary_dark']}; font-size: 12px; font-weight: 500;")
        legend_layout.addWidget(avg_lbl)
        
        layout.addLayout(legend_layout)

        return card

    def _create_timeline_card(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("⏰ 成长时间轴")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        self.timeline_scroll = QScrollArea()
        self.timeline_scroll.setWidgetResizable(True)
        self.timeline_scroll.setFrameShape(QFrame.NoFrame)
        self.timeline_scroll.setStyleSheet("background-color: transparent;")

        self.timeline_container = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.timeline_layout.setSpacing(16)
        self.timeline_scroll.setWidget(self.timeline_container)

        layout.addWidget(self.timeline_scroll, 1)

        return card

    def _create_achievement_card(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("🏆 成就徽章")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        grid = QGridLayout()
        grid.setSpacing(12)

        achievements = [
            ("📚", "小书虫", True),
            ("🧮", "算术达人", True),
            ("🔤", "英语小能手", False),
            ("🏃", "运动健将", False),
            ("🎨", "艺术新星", True),
            ("🌟", "超级明星", False)
        ]

        for i, (icon, name, unlocked) in enumerate(achievements):
            badge = self._create_badge(icon, name, unlocked)
            grid.addWidget(badge, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addStretch()

        return card

    def _create_badge(self, icon, name, unlocked):
        widget = QFrame()
        widget.setFixedHeight(60)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {'#FFF8EC' if unlocked else '#F5F5F5'};
                border-radius: 12px;
                opacity: {'1' if unlocked else '0.5'};
            }}
        """)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)

        name_label = QLabel(name)
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {'#333' if unlocked else '#999'};")
        layout.addWidget(name_label)

        if not unlocked:
            lock_label = QLabel("🔒")
            lock_label.setStyleSheet("font-size: 16px;")
            layout.addWidget(lock_label)

        return widget

    def _create_stats_card(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_label = QLabel("📊 本周数据")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        stats = [
            ("阅读时长", "2.5", "小时", COLORS["primary"]),
            ("完成任务", "5", "个", COLORS["accent"]),
            ("互动次数", "12", "次", COLORS["success"]),
            ("学习单词", "20", "个", COLORS["warning"])
        ]

        for label, value, unit, color in stats:
            stat_row = self._create_stat_row(label, value, unit, color)
            layout.addWidget(stat_row)

        layout.addStretch()

        return card

    def _create_stat_row(self, label, value, unit, color):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary']};
                border-radius: 10px;
                padding: 10px 12px;
            }}
        """)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        dot_label = QLabel("●")
        dot_label.setStyleSheet(f"color: {color}; font-size: 16px;")
        layout.addWidget(dot_label)

        label_text = QLabel(label)
        label_text.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px;")
        layout.addWidget(label_text)

        layout.addStretch()

        value_text = QLabel(f"{value} {unit}")
        value_font = QFont()
        value_font.setBold(True)
        value_text.setFont(value_font)
        value_text.setStyleSheet(f"color: {COLORS['primary_dark']};")
        layout.addWidget(value_text)

        return widget

    def _create_subscription_tab(self):
        self.subscription_tab = QWidget()
        layout = QVBoxLayout(self.subscription_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        self.subs_card = CardWidget()
        subs_layout = QVBoxLayout(self.subs_card)
        subs_layout.setContentsMargins(20, 20, 20, 20)
        subs_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        title_label = QLabel("📚 内容订阅")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        hint_label = QLabel("订阅后机器人会每天推送精选内容")
        hint_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        header_layout.addWidget(hint_label)

        subs_layout.addLayout(header_layout)

        self.subs_scroll = QScrollArea()
        self.subs_scroll.setWidgetResizable(True)
        self.subs_scroll.setFrameShape(QFrame.NoFrame)
        self.subs_scroll.setStyleSheet("background-color: transparent;")

        self.subs_container = QWidget()
        self.subs_layout = QVBoxLayout(self.subs_container)
        self.subs_layout.setContentsMargins(0, 0, 0, 0)
        self.subs_layout.setSpacing(12)
        self.subs_scroll.setWidget(self.subs_container)

        subs_layout.addWidget(self.subs_scroll, 1)

        layout.addWidget(self.subs_card, 1)

    def _add_timeline_item(self, record):
        date = record.get("date", "")
        type_ = record.get("type", "")
        content = record.get("content", "")
        mood = record.get("mood", 5)

        type_icons = {
            "task": "✅",
            "chat": "💬",
            "emotion": "😊",
            "activity": "🏃"
        }
        type_names = {
            "task": "任务完成",
            "chat": "互动记录",
            "emotion": "心情记录",
            "activity": "活动记录"
        }

        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
            }}
        """)
        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        date_col = QVBoxLayout()
        date_col.setSpacing(2)

        date_label = QLabel(date[-5:] if len(date) > 5 else date)
        date_label.setAlignment(Qt.AlignCenter)
        date_font = QFont()
        date_font.setBold(True)
        date_label.setFont(date_font)
        date_label.setStyleSheet(f"color: {COLORS['primary_dark']}; font-size: 14px; min-width: 50px;")
        date_col.addWidget(date_label)

        dot_label = QLabel("●")
        dot_label.setAlignment(Qt.AlignCenter)
        dot_label.setStyleSheet(f"color: {COLORS['primary']}; font-size: 14px;")
        date_col.addWidget(dot_label)

        date_col.addStretch()
        layout.addLayout(date_col)

        line = QFrame()
        line.setFixedWidth(2)
        line.setStyleSheet(f"background-color: {COLORS['primary']};")
        layout.addWidget(line)

        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                padding: 12px 16px;
            }}
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(4)

        header_row = QHBoxLayout()

        type_icon = QLabel(type_icons.get(type_, "📝"))
        type_icon.setStyleSheet("font-size: 18px;")
        header_row.addWidget(type_icon)

        type_label = QLabel(type_names.get(type_, "记录"))
        type_font = QFont()
        type_font.setBold(True)
        type_label.setFont(type_font)
        header_row.addWidget(type_label)

        header_row.addStretch()

        mood_label = QLabel("😊" * mood if mood > 0 else "😢")
        mood_label.setStyleSheet("font-size: 14px;")
        header_row.addWidget(mood_label)

        content_layout.addLayout(header_row)

        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px;")
        content_layout.addWidget(content_label)

        layout.addWidget(content_frame, 1)

        self.timeline_layout.addWidget(item)

    def _add_subscription_item(self, sub):
        id_ = sub.get("id", 0)
        icon = sub.get("icon", "📚")
        title = sub.get("title", "")
        description = sub.get("description", "")
        subscribed = sub.get("subscribed", False)

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
        layout.setSpacing(14)

        icon_label = QLabel(icon)
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: white;
                border-radius: 24px;
                font-size: 24px;
            }}
        """)
        layout.addWidget(icon_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        info_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        info_layout.addWidget(desc_label)

        layout.addLayout(info_layout, 1)

        switch = SwitchButton()
        switch.setChecked(subscribed)
        switch.toggled.connect(lambda checked, sid=id_: self._toggle_subscription(sid, checked))
        layout.addWidget(switch)

        self.subs_layout.addWidget(item)

    def _toggle_subscription(self, sub_id, checked):
        from PySide6.QtWidgets import QMessageBox
        status = "订阅" if checked else "取消订阅"
        QMessageBox.information(self, "成功", f"{status}成功！")

    def load_data(self):
        result = self.main_window.api_client.get_growth_records()
        if result.get("code") == 0:
            self.records = result.get("data", [])
            
            while self.timeline_layout.count():
                child = self.timeline_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            mood_data = []
            for record in self.records:
                self._add_timeline_item(record)
                mood_data.append(record.get("mood", 4))
            
            self.mood_chart.set_mood_data(mood_data[-7:] if len(mood_data) >= 7 else mood_data)
            self.timeline_layout.addStretch()

        result = self.main_window.api_client.get_subscriptions()
        if result.get("code") == 0:
            self.subscriptions = result.get("data", [])
            
            while self.subs_layout.count():
                child = self.subs_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            for sub in self.subscriptions:
                self._add_subscription_item(sub)
            
            self.subs_layout.addStretch()


class MoodChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mood_data = [4, 5, 4, 5, 5, 4, 5]
        self.days = ["一", "二", "三", "四", "五", "六", "日"]

    def set_mood_data(self, data):
        if len(data) > 0:
            self.mood_data = data + [4] * (7 - len(data)) if len(data) < 7 else data[-7:]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        padding = 40
        chart_w = w - padding * 2
        chart_h = h - padding - 10

        painter.setPen(QPen(QColor(COLORS["border"]), 1, Qt.DashLine))
        for i in range(1, 5):
            y = padding + (chart_h / 4) * i
            painter.drawLine(padding, y, w - padding, y)

        if len(self.mood_data) == 0:
            return

        points = []
        step = chart_w / (len(self.mood_data) - 1)
        for i, mood in enumerate(self.mood_data):
            x = padding + step * i
            y = padding + chart_h - (chart_h / 4) * (mood - 1)
            points.append((x, y))

        if len(points) >= 2:
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            
            for i in range(1, len(points)):
                prev_x, prev_y = points[i-1]
                x, y = points[i]
                ctrl_x = (prev_x + x) / 2
                path.quadTo(ctrl_x, prev_y, ctrl_x, (prev_y + y) / 2)
                path.quadTo(ctrl_x, y, x, y)

            grad = QLinearGradient(0, padding, 0, h - 20)
            grad.setColorAt(0, QColor(142, 215, 196, 80))
            grad.setColorAt(1, QColor(142, 215, 196, 0))
            
            fill_path = QPainterPath(path)
            fill_path.lineTo(points[-1][0], h - 20)
            fill_path.lineTo(points[0][0], h - 20)
            fill_path.close()
            
            painter.fillPath(fill_path, QBrush(grad))
            painter.setPen(QPen(QColor(COLORS["primary"]), 3))
            painter.drawPath(path)

        for i, (x, y) in enumerate(points):
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor("white")))
            painter.drawEllipse(x - 6, y - 6, 12, 12)
            
            painter.setBrush(QBrush(QColor(COLORS["primary"])))
            painter.drawEllipse(x - 4, y - 4, 8, 8)

        painter.setPen(QPen(QColor(COLORS["text_light"])))
        painter.setFont(QFont("Microsoft YaHei", 11))
        for i in range(len(self.days)):
            x = padding + step * i
            painter.drawText(QRectF(x - 20, h - 20, 40, 20), Qt.AlignCenter, f"周{self.days[i]}")
