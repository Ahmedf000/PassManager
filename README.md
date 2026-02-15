
#  Secure Vault — Password Manager

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-cyan?style=flat-square)](https://pypi.org/project/PyQt5)
[![Cryptography](https://img.shields.io/badge/Cryptography-AES256-green?style=flat-square)](https://cryptography.io)


A secure, encrypted password manager with a futuristic neon UI.
Each team member has their own vault protected by a master password.

---

##  Quick Start

pip install -r requirements.txt
python main.py

---

##  Change Theme

Open `config.yml` and set `theme.name` to one of:
- `blue`   (default neon blue)
- `pink`   (hot pink cyberpunk)
- `green`  (matrix green)
- `purple` (deep purple neon)

---

##  Security

- AES-256 encryption via Fernet
- PBKDF2 key derivation (480,000 iterations)
- Unique random salt per vault
- Master password never stored
- Auto-clears clipboard after 30 seconds

---

##  Build EXE

pyinstaller --onefile --windowed --name SecureVault main.py
