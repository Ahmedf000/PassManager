import sys
from PyQt5.QtWidgets import QApplication
from crypto_manager import CryptoManager
from config_manager import ConfigManager
from gui.login_window import LoginWindow
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    config = ConfigManager()
    crypto = CryptoManager()

    login = LoginWindow(crypto, config)

    if login.exec_() and login.is_auth:
        window = MainWindow(crypto, config)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()