import json
import secrets
import string
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class CryptoManager:
    def __init__(self):
        self.vault_dir = Path.home() / ".password_vault"
        self.vault_dir.mkdir(exist_ok=True)
        self.vault_file = self.vault_dir / "vault.encrypted"
        self.salt_file  = self.vault_dir / "vault.salt"
        self.passwords  = {}
        self.fernet     = None


    def derive_key(self, master_pass: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_pass.encode()))
        return key



    def vault_exists(self) -> bool:
        return self.vault_file.exists() and self.salt_file.exists()



    def create_vault(self, master_pass: str) -> tuple[bool, str]:
        try:
            if len(master_pass) < 8:
                return False, "Password must be at least 8 characters"
            salt = secrets.token_bytes(32)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            key          = self.derive_key(master_pass, salt)
            self.fernet  = Fernet(key)
            self.passwords = {}
            self.save_vault()
            return True, "Vault created successfully"
        except Exception as e:
            return False, f"Failed to create vault: {e}"



    def unlock_vault(self, master_pass: str) -> tuple[bool, str]:
        try:
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
            key         = self.derive_key(master_pass, salt)
            self.fernet = Fernet(key)
            with open(self.vault_file, 'rb') as f:
                encrypted = f.read()
            decrypted       = self.fernet.decrypt(encrypted)
            self.passwords  = json.loads(decrypted.decode())  # ← FIX: was never assigned
            return True, "Vault unlocked"
        except Exception:
            return False, "Incorrect password"




    def save_vault(self):
        data      = json.dumps(self.passwords, indent=2)
        encrypted = self.fernet.encrypt(data.encode())
        with open(self.vault_file, 'wb') as f:
            f.write(encrypted)




    def add_password(self, service: str, username: str, password: str, notes: str = ""):
        self.passwords[service] = {
            "username": username,
            "password": password,
            "notes":    notes,
        }
        self.save_vault()




    def delete_password(self, service: str) -> bool:
        if service in self.passwords:
            del self.passwords[service]
            self.save_vault()
            return True
        return False



    def get_password(self, service: str) -> dict:
        return self.passwords.get(service, None)



    def get_all_services(self) -> list:
        return sorted(self.passwords.keys())




    def generate_password(self, length: int = 16) -> str:
        chars = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
        return ''.join(secrets.choice(chars) for _ in range(length))



