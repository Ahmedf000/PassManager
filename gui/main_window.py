from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QLineEdit,
                             QTextEdit, QDialog, QMessageBox, QSpinBox,
                             QListWidgetItem, QInputDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
import pyperclip

import crypto_manager

"""
Pyperclip is a cross-platform 
Python module for copy and paste clipboard functions.
"""


class AddPasswordDialog(QDialog):
    def __init__(self, crypto_manager,parent=None, edit_service=None):
        super().__init__(parent)
        self.crypto_manager = crypto_manager
        self.edit_service = edit_service
        self.init_ui()

        if edit_service:
            data = crypto_manager.get_password(edit_service)
            if data:
                self.service_input.setText(edit_service)
                self.service_input.setReadOnly(True)
                self.username_input.setText(data['username'])
                self.password_input.setText(data['password'])
                self.notes_input.setText(data['notes'])




    def init_ui(self):
        title = "EDIT ENTRY" if self.edit_service else "NEW ENTRY"
        self.setWindowTitle(title)
        self.setFixedSize(500, 450)
        self.setStyleSheet("""
        """)

        vbox = QVBoxLayout()
        vbox.setSpacing(12)
        vbox.setContentsMargins(20, 20, 20, 20)


        #SERVICE NAME
        vbox.addWidget(QLabel("▸ SERVICE NAME"))
        self.service_input = QLineEdit()
        self.service_input.setPlaceholderText("Gmail, Facebook, Any...")
        vbox.addWidget(self.service_input)


        #username
        vbox.addWidget(QLabel("▸ USERNAME / EMAIL"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("user@example....")
        vbox.addWidget(self.username_input)


        #password INPUTS
        vbox.addWidget(QLabel("▸ PASSWORD"))
        pw_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter or Generate ....")
        pw_layout.addWidget(self.password_input)


        #GENERATE
        self.generate_button = QPushButton("▸ GENERATE PASSWORD")
        self.generate_button.setObjectName('generate_button')
        self.generate_button.setFixedWidth(120)
        self.generate_button.clicked.connect(self.generate_password)
        vbox.addWidget(self.generate_button)


        #SHOW CHECKBOX
        self.show_btn = QPushButton("◉ SHOW")
        self.show_btn.setCheckable(True)
        self.show_btn.setFixedWidth(120)
        self.show_btn.toggled.connect(self.toggle_pass_visibility)
        vbox.addWidget(self.show_btn)




        #NOTES
        vbox.addWidget(QLabel("▸ NOTES"))
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Add your notes here...")
        vbox.addWidget(self.notes_input)


        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("◀ CANCEL")
        cancel_btn.clicked.connect(self.save_password)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("▼ SAVE ▼")
        self.save_btn.clicked.connect(self.save_password)
        btn_layout.addWidget(save_btn)

        vbox.addLayout(btn_layout)
        self.setLayout(vbox)
        self.service_input.setFocus()





    def toggle_pass_visibility(self, checked):

        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_btn.setText("◉ HIDE")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_btn.setText("◉ SHOW")




    def generate_password(self):
        length, ok = QInputDialog.getInt(self, "Password Length:  ",
                                         "Enter a password length: ", 16, 8, 64, 1)

        if ok:
            password = self.crypto_manager.generate_password(length)
            self.password_input.setText(password)
            QMessageBox.information(self, "Password Generated",
                                    f"Strong Password generated!\nLength: {length} characters")





    def save_password(self):
        service = self.service_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        notes = self.notes_input.text().strip()

        if not service:
            QMessageBox.warning(self, "ERROR", "Service Name is required!")
            return
        if not username:
            QMessageBox.warning(self, "ERROR","Username is required!")
            return
        if not password:
            QMessageBox.warning(self, "ERROR", "Password is required!")
            return

        if not self.edit_service and service in crypto_manager.passwords:
            reply = QMessageBox.question(self, "Service Exists",
                                         f"'{service}' already exists. Overwrite?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return

        self.crypto_manager.add_password(service, username, password, notes)
        self.accept()






class MainWindow(QMainWindow):
    def __init__(self, crypto_manager):
        super().__init__()
        self.crypto_manager = crypto_manager
        self.current_service = None
        self.init_ui()
        self.load_passwords()




    def init_ui(self):
        self.setWindowTitle("SECURE VAULT SYSTEM")
        self.setGeometry(100, 100, 100, 650)
        self.setStyleSheet("""
        """)

        central = QWidget()
        self.setCentralWidget(central)

        main_vbox = QHBoxLayout()
        main_vbox.setSpacing(15)
        main_vbox.setContentsMargins(15, 15, 15, 15)


        left_panel = QVBoxLayout()


        """SEARCH BAR ON THE LEFT"""
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("SEARCH DATABASE...")
        self.search_input.textChanged.connect(self.filter_passwords)
        left_panel.addWidget(self.search_input)


        """PASSWORD LIST"""
        self.password_list = QListWidget()
        self.password_list.itemClicked.connect(self.show_passwords_details)
        left_panel.addWidget(self.password_list)


        add_btn = QPushButton("◢ ADD NEW ENTRY ◣")
        add_btn.clicked.connect(self.add_password)
        left_panel.addWidget(add_btn)


        right_panel = QVBoxLayout()



        #TITLE
        title = QLabel("◢ ENTRY DETAILS ◣")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #00ffff; letter-spacing: 3px;")
        right_panel.addWidget(title)


        self.details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_layout.setSpacing(15)


    def set_details_enabled(self, enabled):
        self.show_btn.setEnabled(enabled)
        self.copy_btn.setEnabled(enabled)
        self.edit_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)





    def load_passwords(self):
        self.password_list.clear()
        services = self.crypto_manager.get_all_services()

        if not services:
            item = QListWidgetItem("DATABASE EMPTY")
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(QColor("#0099cc"))
            self.password_list.addItem(item)
        else:
            for service in services:
                data = self.crypto_manager.get_password(service)
                item = QListWidgetItem(f"▸ {service.upper()}")
                item.setData(Qt.UserRole, service)
                self.password_list.addItem(item)





    def filter_passwords(self, text):
        for i in range(self.password_list.count()):
            item = self.password_list.item(i)
            service = item.data(Qt.UserRole)
            if service:
                item.setHidden(text.lower() not in service.lower())





    def show_passwords_details(self, item):
        service = item.data(Qt.UserRole)
        if not service:
            return

        self.current_service = service
        data = self.crypto_manager.get_password(service)

        if data:
            self.service_label.setText(service)
            self.username_display.setText(data['username'])
            self.password_display.setText(data['password'])
            self.notes_display.setText(data['notes'])
            self.set_details_enabled(True)

            # Reset password visibility
            self.show_btn.setChecked(False)
            self.password_display.setEchoMode(QLineEdit.Password)




    def toggle_passwords(self, checked):
        if checked:
            self.password_display.setEchoMode(QLineEdit.Normal)
        else:
            self.password_display.setEchoMode(QLineEdit.Password)





    def copy_passwords(self):
        if self.current_service:
            data = self.crypto_manager.get_password(self.current_service)
            if data:
                pyperclip.copy(data['password'])
                self.statusBar().showMessage("◢ PASSWORD COPIED TO CLIPBOARD ◣", 3000)






    def add_password(self):
        dialog = AddPasswordDialog(self.crypto_manager, self)
        if dialog.exec_():
            self.load_passwords()
            self.statusBar().showMessage("◢ ENTRY ADDED SUCCESSFULLY ◣", 3000)






    def edit_password(self):
        if self.current_service:
            dialog = AddPasswordDialog(self.crypto_manager, self, self.current_service)
            if dialog.exec_():
                self.load_passwords()
                self.show_password_details(self.password_list.currentItem())
                self.statusBar().showMessage("◢ ENTRY UPDATED SUCCESSFULLY ◣", 3000)






    def delete_password(self):
        if self.current_service:
            reply = QMessageBox.question(self, "◢ CONFIRM DELETE ◣",
                                         f"Delete entry for '{self.current_service}'?\n\nThis action cannot be undone.",
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











