from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit,
                             QPushButton, QMessageBox, QLabel)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class LoginWindow(QDialog):
    def __init__(self, crypto_manager, config_manager):
        super().__init__()
        self.crypto_manager  = crypto_manager
        self.config_manager  = config_manager
        self.is_auth         = False
        self.init_ui()

    def init_ui(self):
        cfg = self.config_manager.get_app()
        self.setWindowTitle(f"{cfg.get('title','SECURE VAULT')} — LOGIN")
        self.setFixedSize(450, 300)
        self.setStyleSheet(self.config_manager.get_stylesheet())

        vbox = QVBoxLayout()
        vbox.setSpacing(15)
        vbox.setContentsMargins(35, 35, 35, 35)

        title = QLabel("◢ SECURE VAULT ◣")
        f = QFont()
        f.setPointSize(20)
        f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignCenter)
        c = self.config_manager.get_colors()
        title.setStyleSheet(f"color: {c['accent_bright']}; letter-spacing: 3px;")
        vbox.addWidget(title)

        subtitle = QLabel(
            "▼ AUTHORIZATION REQUIRED ▼" if self.crypto_manager.vault_exists()
            else "▼ INITIALIZE NEW VAULT ▼"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {c['accent_dim']}; font-size: 11px; letter-spacing: 2px;")
        vbox.addWidget(subtitle)

        vbox.addSpacing(5)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("▸ ENTER ACCESS CODE")
        self.password_input.returnPressed.connect(self.handle_login)
        vbox.addWidget(self.password_input)

        if not self.crypto_manager.vault_exists():
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.setPlaceholderText("▸ CONFIRM ACCESS CODE")
            self.confirm_input.returnPressed.connect(self.handle_login)
            vbox.addWidget(self.confirm_input)
        else:
            self.confirm_input = None  # ← FIX: was True

        self.login_btn = QPushButton(
            "◢ UNLOCK ◣" if self.crypto_manager.vault_exists() else "◢ CREATE VAULT ◣"
        )
        self.login_btn.clicked.connect(self.handle_login)
        vbox.addWidget(self.login_btn)

        self.setLayout(vbox)
        self.password_input.setFocus()

    def handle_login(self):
        password = self.password_input.text()

        if not password:
            QMessageBox.warning(self, "ERROR", "Please enter a password")
            return

        if self.crypto_manager.vault_exists():
            success, message = self.crypto_manager.unlock_vault(password)
            if success:
                self.is_auth = True
                self.accept()
            else:
                QMessageBox.critical(self, "ACCESS DENIED", "Incorrect password!")
                self.password_input.clear()
                self.password_input.setFocus()
        else:
            confirm = self.confirm_input.text()
            if password != confirm:
                QMessageBox.warning(self, "ERROR", "Passwords do not match!")
                return
            success, message = self.crypto_manager.create_vault(password)
            if success:
                QMessageBox.information(self, "VAULT CREATED",
                    "Vault initialized!\n\n Remember your password — it cannot be recovered!")
                self.is_auth = True
                self.accept()
            else:
                QMessageBox.critical(self, "ERROR", message)
