import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from config import FONT_FAMILY
from ui.login_page import LoginPage
from ui.main_window import MainWindow
from db.database import Database
from services.auth_service import AuthService


def main():
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    
    font = QFont(FONT_FAMILY)
    font.setPointSize(10)
    app.setFont(font)
    
    db = Database()
    db.init_db()
    
    auth_service = AuthService(db)
    
    if auth_service.has_valid_token():
        window = MainWindow(db, auth_service)
        window.show()
    else:
        login = LoginPage(db, auth_service)
        login.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
