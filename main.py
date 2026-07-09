import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, 
    QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QGridLayout,
    QSplashScreen, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer
from PySide6.QtGui import QPixmap
from database import initialize_db
import auth
from inventory_ui import InventoryDashboard

class LoginRegisterView(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.setObjectName("loginView")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        card = QWidget(self)
        card.setObjectName("loginCard")
        card_layout = QGridLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(24, 24, 24, 24)
        
        self.title_lbl = QLabel("🛡️ Inventory Control Access")
        self.title_lbl.setObjectName("windowTitle")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedWidth(260)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(260)
        
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("signInBtn")
        self.register_btn = QPushButton("Create Secure Account")
        self.register_btn.setObjectName("registerBtn")
        
        card_layout.addWidget(self.title_lbl, 0, 0, 1, 2, Qt.AlignCenter)
        card_layout.addWidget(self.username_input, 1, 0, 1, 2, Qt.AlignCenter)
        card_layout.addWidget(self.password_input, 2, 0, 1, 2, Qt.AlignCenter)
        card_layout.addWidget(self.login_btn, 3, 0)
        card_layout.addWidget(self.register_btn, 3, 1)
        
        layout.addWidget(card, 0, 0, Qt.AlignCenter)
        
        self.login_btn.clicked.connect(self.attempt_login)
        self.register_btn.clicked.connect(self.attempt_register)

    def attempt_login(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text()
        
        user_id = auth.authenticate_user(user, pwd)
        if user_id is not None:
            self.username_input.clear()
            self.password_input.clear()
            self.on_login_success(user_id)
        else:
            QMessageBox.critical(self, "Access Denied", "Invalid username or password credentials.")

    def attempt_register(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text()
        
        success, msg = auth.register_user(user, pwd)
        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.warning(self, "System Error", msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory management system")
        self.resize(850, 550)
        
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)
        
        self.auth_view = LoginRegisterView(on_login_success=self.show_dashboard)
        self.dashboard_view = None
        
        self.central_stack.addWidget(self.auth_view)
        self.central_stack.setCurrentWidget(self.auth_view)

    def show_dashboard(self, user_id):
        self.dashboard_view = InventoryDashboard(user_id=user_id, logout_callback=self.show_login)
        self.central_stack.addWidget(self.dashboard_view)
        
        eff = QGraphicsOpacityEffect(self.dashboard_view)
        self.dashboard_view.setGraphicsEffect(eff)
        self.central_stack.setCurrentWidget(self.dashboard_view)
        
        anim = QPropertyAnimation(eff, b"opacity")
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        self.transition_anim = anim
        anim.start()

    def show_login(self):
        if self.dashboard_view:
            self.central_stack.removeWidget(self.dashboard_view)
            self.dashboard_view.deleteLater()
            self.dashboard_view = None
            
        eff = QGraphicsOpacityEffect(self.auth_view)
        self.auth_view.setGraphicsEffect(eff)
        self.central_stack.setCurrentWidget(self.auth_view)
        
        anim = QPropertyAnimation(eff, b"opacity")
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        self.transition_anim = anim
        anim.start()


DARK_STYLE = """
QWidget {
    background-color: #0f172a;
    color: #f1f5f9;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

QWidget#loginView {
    background-image: url("assets/login_bg.png");
    background-position: center;
    background-repeat: no-repeat;
}

QWidget#loginCard {
    background-color: rgba(15, 23, 42, 0.85);
    border: 1px solid #334155;
    border-radius: 8px;
}

QMainWindow, QDialog {
    background-color: #0f172a;
}

QLabel#windowTitle {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
    margin-top: 10px;
    margin-bottom: 15px;
}

QLabel#dashboardTitle {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}

QLineEdit {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 6px 10px;
}
QLineEdit:focus {
    border: 1px solid #6366f1;
    background-color: #1e293b;
}
QLineEdit:placeholder {
    color: #64748b;
}

QSpinBox, QDoubleSpinBox {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 5px 8px;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #6366f1;
    background-color: #1e293b;
}

QPushButton {
    background-color: #334155;
    color: #ffffff;
    border: 1px solid #475569;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: 600;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #475569;
    border-color: #64748b;
}
QPushButton:pressed {
    background-color: #1e293b;
    border-color: #475569;
}

QPushButton#signInBtn {
    background-color: #3b82f6;
    border: 1px solid #2563eb;
}
QPushButton#signInBtn:hover {
    background-color: #2563eb;
    border-color: #1d4ed8;
}
QPushButton#signInBtn:pressed {
    background-color: #1d4ed8;
}

QPushButton#registerBtn {
    background-color: #10b981;
    border: 1px solid #059669;
}
QPushButton#registerBtn:hover {
    background-color: #059669;
    border-color: #047857;
}
QPushButton#registerBtn:pressed {
    background-color: #047857;
}

QPushButton#addButton {
    background-color: #4f46e5;
    border: 1px solid #4338ca;
}
QPushButton#addButton:hover {
    background-color: #4338ca;
    border-color: #3730a3;
}
QPushButton#addButton:pressed {
    background-color: #3730a3;
}

QPushButton#editButton {
    background-color: #475569;
    border: 1px solid #334155;
}
QPushButton#editButton:hover {
    background-color: #334155;
    border-color: #1e293b;
}
QPushButton#editButton:pressed {
    background-color: #1e293b;
}

QPushButton#sellButton {
    background-color: #f59e0b;
    border: 1px solid #d97706;
}
QPushButton#sellButton:hover {
    background-color: #d97706;
    border-color: #b45309;
}
QPushButton#sellButton:pressed {
    background-color: #b45309;
}

QPushButton#deleteButton {
    background-color: #ef4444;
    border: 1px solid #dc2626;
}
QPushButton#deleteButton:hover {
    background-color: #dc2626;
    border-color: #b91c1c;
}
QPushButton#deleteButton:pressed {
    background-color: #b91c1c;
}

QPushButton#refreshButton {
    background-color: #1e293b;
    border: 1px solid #334155;
}
QPushButton#refreshButton:hover {
    background-color: #334155;
    border-color: #475569;
}
QPushButton#refreshButton:pressed {
    background-color: #0f172a;
}

QPushButton#logoutBtn {
    background-color: #ef4444;
    border: 1px solid #dc2626;
    font-size: 12px;
    padding: 4px 8px;
}
QPushButton#logoutBtn:hover {
    background-color: #dc2626;
    border-color: #b91c1c;
}
QPushButton#logoutBtn:pressed {
    background-color: #b91c1c;
}

QTableWidget {
    background-color: #1e293b;
    color: #e2e8f0;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 4px;
}
QTableWidget::item {
    padding: 5px;
}
QTableWidget::item:selected {
    background-color: #312e81;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #0f172a;
    color: #cbd5e1;
    padding: 6px;
    border: 1px solid #334155;
    font-weight: bold;
}
QScrollBar:vertical {
    border: none;
    background: #0f172a;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

if __name__ == "__main__":
    initialize_db()
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    
    window = MainWindow()
    
    pixmap = QPixmap("assets/splash.png")
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.show()
    
    splash.setWindowOpacity(0.0)
    app.fade_in = QPropertyAnimation(splash, b"windowOpacity")
    app.fade_in.setDuration(800)
    app.fade_in.setStartValue(0.0)
    app.fade_in.setEndValue(1.0)
    app.fade_in.start()
    
    def start_main_app():
        app.fade_out = QPropertyAnimation(splash, b"windowOpacity")
        app.fade_out.setDuration(800)
        app.fade_out.setStartValue(1.0)
        app.fade_out.setEndValue(0.0)
        
        def on_fade_out_finished():
            splash.close()
            window.setWindowOpacity(0.0)
            window.show()
            
            app.win_fade = QPropertyAnimation(window, b"windowOpacity")
            app.win_fade.setDuration(600)
            app.win_fade.setStartValue(0.0)
            app.win_fade.setEndValue(1.0)
            app.win_fade.start()
            
        app.fade_out.finished.connect(on_fade_out_finished)
        app.fade_out.start()
        
    QTimer.singleShot(2500, start_main_app)
    
    sys.exit(app.exec())