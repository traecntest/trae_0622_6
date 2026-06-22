from config import COLORS


def get_global_styles():
    return f"""
    * {{
        font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
        color: {COLORS["text"]};
    }}
    
    QMainWindow, QWidget {{
        background-color: {COLORS["secondary"]};
    }}
    
    QPushButton {{
        background-color: {COLORS["primary"]};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 500;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS["primary_dark"]};
    }}
    
    QPushButton:pressed {{
        transform: scale(0.98);
    }}
    
    QPushButton:disabled {{
        background-color: #CCCCCC;
        color: #888888;
    }}
    
    QLineEdit, QTextEdit, QSpinBox, QComboBox {{
        background-color: white;
        border: 2px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 14px;
        selection-background-color: {COLORS["primary"]};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border-color: {COLORS["primary"]};
        outline: none;
    }}
    
    QLabel {{
        color: {COLORS["text"]};
        font-size: 14px;
    }}
    
    QListWidget, QListView {{
        background-color: white;
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 4px;
    }}
    
    QListWidget::item {{
        padding: 12px;
        border-radius: 8px;
        margin: 2px;
    }}
    
    QListWidget::item:hover {{
        background-color: {COLORS["secondary"]};
    }}
    
    QListWidget::item:selected {{
        background-color: {COLORS["primary"]};
        color: white;
    }}
    
    QScrollBar:vertical {{
        background-color: transparent;
        width: 8px;
        margin: 4px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS["primary"]};
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: transparent;
        height: 8px;
        margin: 4px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS["primary"]};
        border-radius: 4px;
        min-width: 20px;
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    QTabWidget::pane {{
        border: none;
        background-color: transparent;
    }}
    
    QTabBar::tab {{
        background-color: transparent;
        padding: 10px 24px;
        font-size: 14px;
        color: {COLORS["text_light"]};
        border-bottom: 2px solid transparent;
    }}
    
    QTabBar::tab:selected {{
        color: {COLORS["primary_dark"]};
        border-bottom-color: {COLORS["primary"]};
    }}
    
    QSlider::groove:horizontal {{
        height: 6px;
        background: {COLORS["border"]};
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background: {COLORS["primary"]};
        width: 18px;
        height: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {COLORS["primary_dark"]};
    }}
    
    QProgressBar {{
        border: none;
        background-color: {COLORS["border"]};
        border-radius: 6px;
        height: 12px;
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background-color: {COLORS["primary"]};
        border-radius: 6px;
    }}
    """


def get_error_input_style():
    return f"""
    QLineEdit {{
        border: 2px solid {COLORS["error"]};
        animation: shake 0.5s ease-in-out;
    }}
    """


def get_accent_button_style():
    return f"""
    QPushButton {{
        background-color: {COLORS["accent"]};
    }}
    QPushButton:hover {{
        background-color: {COLORS["accent_dark"]};
    }}
    """


def get_ghost_button_style():
    return f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS["primary_dark"]};
        border: 2px solid {COLORS["primary"]};
    }}
    QPushButton:hover {{
        background-color: {COLORS["primary"]};
        color: white;
    }}
    """
