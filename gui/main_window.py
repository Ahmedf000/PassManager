
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QLineEdit,
                             QTextEdit, QDialog, QMessageBox, QListWidgetItem,
                             QInputDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
import pyperclip


class AddPasswordDialog(QDialog):
    def __init__(self, crypto_manager, config_manager, parent=None, edit_service=None):
        super().__init__(parent)
        self.crypto_manager = crypto_manager
        self.config_manager = config_manager
        self.edit_service   = edit_service
        self.init_ui()

        if edit_service:
            data = crypto_manager.get_password(edit_service)
            if data:
                self.service_input.setText(edit_service)
                self.service_input.setReadOnly(True)
                self.username_input.setText(data['username'])
                self.password_input.setText(data['password'])
                self.notes_input.setPlainText(data['notes'])

    def init_ui(self):
        self.setWindowTitle("◢ EDIT ENTRY ◣" if self.edit_service else "◢ NEW ENTRY ◣")
        self.setFixedSize(500, 480)
        self.setStyleSheet(self.config_manager.get_stylesheet())

        vbox = QVBoxLayout()
        vbox.setSpacing(12)
        vbox.setContentsMargins(25, 25, 25, 25)

        # Service
        vbox.addWidget(QLabel("▸ SERVICE NAME"))
        self.service_input = QLineEdit()
        self.service_input.setPlaceholderText("Gmail, Facebook, Bank...")
        vbox.addWidget(self.service_input)

        # Username
        vbox.addWidget(QLabel("▸ USERNAME / EMAIL"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("user@example.com")
        vbox.addWidget(self.username_input)

        # Password row
        vbox.addWidget(QLabel("▸ PASSWORD"))
        pw_row = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter or generate...")
        pw_row.addWidget(self.password_input)

        self.generate_btn = QPushButton("◈ GENERATE")
        self.generate_btn.setObjectName("generateBtn")
        self.generate_btn.setFixedWidth(130)
        self.generate_btn.clicked.connect(self.generate_password)
        pw_row.addWidget(self.generate_btn)
        vbox.addLayout(pw_row)

        # Show/hide toggle
        self.show_btn = QPushButton("◉ SHOW")
        self.show_btn.setCheckable(True)
        self.show_btn.setFixedWidth(120)
        self.show_btn.toggled.connect(self.toggle_pass_visibility)
        vbox.addWidget(self.show_btn)

        # Notes
        vbox.addWidget(QLabel("▸ NOTES [OPTIONAL]"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Additional info...")
        self.notes_input.setMaximumHeight(80)
        vbox.addWidget(self.notes_input)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("◀ CANCEL")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("▼ SAVE ▼")
        save_btn.clicked.connect(self.save_password)
        btn_row.addWidget(save_btn)

        vbox.addLayout(btn_row)
        self.setLayout(vbox)
        self.service_input.setFocus()

    def toggle_pass_visibility(self, checked):
        self.password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.show_btn.setText("◉ HIDE" if checked else "◉ SHOW")

    def generate_password(self):
        length, ok = QInputDialog.getInt(self, "Password Length", "Enter length:", 16, 8, 64, 1)
        if ok:
            pwd = self.crypto_manager.generate_password(length)
            self.password_input.setText(pwd)
            QMessageBox.information(self, "GENERATED",
                f"Strong password generated!\nLength: {length} characters")

    def save_password(self):
        service  = self.service_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        notes    = self.notes_input.toPlainText().strip()

        if not service:
            QMessageBox.warning(self, "ERROR", "Service name is required!"); return
        if not username:
            QMessageBox.warning(self, "ERROR", "Username is required!");     return
        if not password:
            QMessageBox.warning(self, "ERROR", "Password is required!");     return

        if not self.edit_service and service in self.crypto_manager.passwords:
            reply = QMessageBox.question(self, "EXISTS",
                f"'{service}' already exists. Overwrite?",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return

        self.crypto_manager.add_password(service, username, password, notes)
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self, crypto_manager, config_manager):
        super().__init__()
        self.crypto_manager  = crypto_manager
        self.config_manager  = config_manager
        self.current_service = None
        self.init_ui()
        self.load_passwords()

    def init_ui(self):
        cfg = self.config_manager.get_app()
        c   = self.config_manager.get_colors()

        self.setWindowTitle(f"◢ {cfg.get('title','SECURE VAULT SYSTEM')} ◣")
        self.setGeometry(100, 100, cfg.get('width', 1000), cfg.get('height', 650))
        self.setStyleSheet(self.config_manager.get_stylesheet())

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ── LEFT PANEL ──────────────────────────────
        left = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("◈ SEARCH DATABASE...")
        self.search_input.textChanged.connect(self.filter_passwords)
        left.addWidget(self.search_input)

        self.password_list = QListWidget()
        self.password_list.itemClicked.connect(self.show_password_details)
        left.addWidget(self.password_list)

        add_btn = QPushButton("◢ ADD NEW ENTRY ◣")
        add_btn.clicked.connect(self.add_password)
        left.addWidget(add_btn)

        # ── RIGHT PANEL ─────────────────────────────
        right = QVBoxLayout()

        title = QLabel("◢ ENTRY DETAILS ◣")
        tf = QFont(); tf.setPointSize(16); tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet(f"color: {c['accent_bright']}; letter-spacing: 3px;")
        right.addWidget(title)

        details_layout = QVBoxLayout()
        details_layout.setSpacing(12)

        details_layout.addWidget(QLabel("▸ SERVICE"))
        self.service_label = QLabel("[ SELECT ENTRY FROM DATABASE ]")
        self.service_label.setStyleSheet(
            f"font-size: 15px; font-weight: bold; color: {c['accent_bright']};"
            f"padding: 10px; border: 1px solid {c['accent_dark']}; border-radius: 5px;"
            f"background-color: rgba(0,217,255,0.05);"
        )
        details_layout.addWidget(self.service_label)

        details_layout.addWidget(QLabel("▸ USERNAME"))
        self.username_display = QLineEdit()
        self.username_display.setReadOnly(True)
        details_layout.addWidget(self.username_display)

        details_layout.addWidget(QLabel("▸ PASSWORD"))
        pw_row = QHBoxLayout()
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setEchoMode(QLineEdit.Password)
        pw_row.addWidget(self.password_display)

        self.show_btn = QPushButton("◉")
        self.show_btn.setCheckable(True)
        self.show_btn.setFixedWidth(50)
        self.show_btn.toggled.connect(self.toggle_password)
        pw_row.addWidget(self.show_btn)
        details_layout.addLayout(pw_row)

        self.copy_btn = QPushButton("◢ COPY TO CLIPBOARD ◣")
        self.copy_btn.clicked.connect(self.copy_password)
        details_layout.addWidget(self.copy_btn)

        details_layout.addWidget(QLabel("▸ NOTES"))
        self.notes_display = QTextEdit()
        self.notes_display.setReadOnly(True)
        self.notes_display.setMaximumHeight(100)
        details_layout.addWidget(self.notes_display)

        details_layout.addStretch()

        btn_row = QHBoxLayout()
        self.edit_btn = QPushButton("◈ EDIT")
        self.edit_btn.clicked.connect(self.edit_password)
        btn_row.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("◈ DELETE")
        self.delete_btn.setObjectName("deleteBtn")
        self.delete_btn.clicked.connect(self.delete_password)
        btn_row.addWidget(self.delete_btn)
        details_layout.addLayout(btn_row)

        details_widget = QWidget()
        details_widget.setLayout(details_layout)
        right.addWidget(details_widget)

        main_layout.addLayout(left, 1)
        main_layout.addLayout(right, 2)
        central.setLayout(main_layout)

        self.set_details_enabled(False)



    def set_details_enabled(self, enabled):
        self.show_btn.setEnabled(enabled)
        self.copy_btn.setEnabled(enabled)
        self.edit_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)




    def load_passwords(self):
        self.password_list.clear()
        services = self.crypto_manager.get_all_services()
        if not services:
            item = QListWidgetItem("◇ DATABASE EMPTY ◇")
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(QColor(self.config_manager.get_colors()['accent_dim']))
            self.password_list.addItem(item)
        else:
            for svc in services:
                item = QListWidgetItem(f"▸ {svc.upper()}")
                item.setData(Qt.UserRole, svc)
                self.password_list.addItem(item)




    def filter_passwords(self, text):
        for i in range(self.password_list.count()):
            item    = self.password_list.item(i)
            service = item.data(Qt.UserRole)
            if service:
                item.setHidden(text.lower() not in service.lower())



    def show_password_details(self, item):
        service = item.data(Qt.UserRole)
        if not service:
            return
        self.current_service = service
        data = self.crypto_manager.get_password(service)
        if data:
            self.service_label.setText(service)
            self.username_display.setText(data['username'])
            self.password_display.setText(data['password'])
            self.notes_display.setPlainText(data['notes'])
            self.set_details_enabled(True)
            self.show_btn.setChecked(False)
            self.password_display.setEchoMode(QLineEdit.Password)



    def toggle_password(self, checked):
        self.password_display.setEchoMode(
            QLineEdit.Normal if checked else QLineEdit.Password)



    def copy_password(self):
        if self.current_service:
            data = self.crypto_manager.get_password(self.current_service)
            if data:
                pyperclip.copy(data['password'])
                self.statusBar().showMessage("◢ PASSWORD COPIED TO CLIPBOARD ◣", 3000)
                # Auto-clear clipboard
                secs = self.config_manager.get_app().get('clipboard_clear_seconds', 30)
                QTimer.singleShot(secs * 1000, lambda: pyperclip.copy(""))



    def add_password(self):
        dialog = AddPasswordDialog(self.crypto_manager, self.config_manager, self)
        if dialog.exec_():
            self.load_passwords()
            self.statusBar().showMessage("◢ ENTRY ADDED SUCCESSFULLY ◣", 3000)



    def edit_password(self):
        if self.current_service:
            dialog = AddPasswordDialog(
                self.crypto_manager, self.config_manager, self, self.current_service)
            if dialog.exec_():
                self.load_passwords()
                self.show_password_details(self.password_list.currentItem())
                self.statusBar().showMessage("◢ ENTRY UPDATED SUCCESSFULLY ◣", 3000)


    def delete_password(self):
        if self.current_service:
            reply = QMessageBox.question(self, "◢ CONFIRM DELETE ◣",
                f"Delete '{self.current_service}'?\n\nThis cannot be undone.",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.crypto_manager.delete_password(self.current_service)
                self.load_passwords()
                self.service_label.setText("[ SELECT ENTRY FROM DATABASE ]")
                self.username_display.clear()
                self.password_display.clear()
                self.notes_display.clear()
                self.current_service = None
                self.set_details_enabled(False)
                self.statusBar().showMessage("◢ ENTRY DELETED SUCCESSFULLY ◣", 3000)