import sys

from PyQt5.QtWidgets import QApplication
from crypto_manager import CryptoManager
from gui.login_window import LoginWindow
from gui.main_window import MainWindow




def main():
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    crypto = CryptoManager()

    login = LoginWindow(crypto)

    if login.exec_() and login.is_auth:
        Window = MainWindow(crypto)
        Window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)



if __name__ == '__main__':
    main()
