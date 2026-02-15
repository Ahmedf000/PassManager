from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QMessageBox, QLabel)

from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt



class LoginWindow(QDialog): #QDialog used to collect quick response from user
    def __init__(self, crypto_manager):
        super().__init__()
        self.crypto_manager = crypto_manager
        self.is_auth = False
        self.init_ui()





    def init_ui(self):
        self.setWindowTitle("Secure Vault - Login")
        self.setFixedSize(400, 280)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0e27, stop:1 #16213e);
                border: 2px solid #00d9ff;
            }
            QLabel {
                color: #00d9ff;
                font-size: 14px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #1a5f7a;
                border-radius: 8px;
                background-color: rgba(10, 25, 47, 0.8);
                color: #00d9ff;
                font-size: 13px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QLineEdit:focus {
                border: 2px solid #00d9ff;
                background-color: rgba(0, 217, 255, 0.05);
                box-shadow: 0 0 15px rgba(0, 217, 255, 0.5);
            }
            QPushButton {
                padding: 12px;
                border: 2px solid #00d9ff;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a5f7a, stop:1 #0d2b3e);
                color: #00d9ff;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00d9ff, stop:1 #1a5f7a);
                color: #0a0e27;
                box-shadow: 0 0 20px rgba(0, 217, 255, 0.8);
            }
            QPushButton:pressed {
                background-color: #003d52;
                border: 2px solid #00ffff;
            }
        """)

        vbox = QVBoxLayout()
        vbox.setSpacing(15)
        vbox.setContentsMargins(30, 30, 30, 30)

        title = QLabel("SECURE VAULT")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00ffff; text-shadow: 0 0 10px #00d9ff;")
        vbox.addWidget(title)


        if self.crypto_manager.vault_exists():
            subtitle = QLabel("▼ AUTHORIZATION REQUIRED ▼")
        else:
            subtitle = QLabel("▼ INITIALIZE NEW VAULT ▼")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #0099cc; font-size: 11px; letter-spacing: 2px;")
        vbox.addWidget(subtitle)

        vbox.addSpacing(10)


        #PASSWORD INPUT FIELD
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("ENTER ACCESS CODE")
        vbox.addWidget(self.password_input)


        #IF NEW VAULT
        if not self.crypto_manager.vault_exists():
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.setPlaceholderText("CONFIRM ACCESS CODE")
            #HANDLE LOGIN
            vbox.addWidget(self.confirm_input)
        else:
            self.confirm_input = True

        vbox.addSpacing(10)


        #login button
        self.login_btn = QPushButton("UNLOCK" if self.crypto_manager.vault_exists() else "CREATE VAULT")
        self.login_btn.clicked.connect(self.handle_login)
        vbox.addWidget(self.login_btn)


        self.setLayout(vbox)
        self.password_input.setFocus()




    def handle_login(self):
        password = self.password_input.text()

        if not password:
            QMessageBox.warning(self, "ERROR","Please enter a password")


        if self.crypto_manager.vault_exists():
            success, message = self.crypto_manager.unlock_vault(password)
            if success:
                self.is_auth = True
                self.accept()
            else:
                QMessageBox.warning(self, "ERROR","Incorrect password")
                self.password_input.clear()
                self.password_input.setFocus()
        else:
            confirm_password = self.confirm_input.text()

            if password != confirm_password:
                QMessageBox.warning(self, "ERROR","Passwords do not match")
                return

            success, message = self.crypto_manager.create_vault(password)
            if success:
                QMessageBox.information(self, "Success", "Vault created successfully!\n\n Remember your password - it cannot be recovered!")
                self.is_auth = True
                self.accept()
            else:
                QMessageBox.critical(self, "ERROR",message)















