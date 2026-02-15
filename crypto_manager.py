import os
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
        self.vault_dir.mkdir(exist_ok=True) #using Pathlib for dir exists as it offers obj-orien appraoch
        self.vault_file = self.vault_dir / "vault.encrypted"
        self.salt_file = self.vault_dir / "vault.salt"
        self.passwords = {}
        self.fernet = None #Uses the same secret key to lock and unlock/ symm


    def derive_key(self, master_pass: str, salt: bytes) -> bytes: #func expected to return bytes
        """
        we use derive key to generate a new cryptographic key from existing
        secret material using a mathematical func
        which to derive the key from the MASTER PASSWORD

        """

        derive_key = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )

        key = base64.urlsafe_b64encode(derive_key.derive(master_pass.encode()))





    def vault_exists(self) -> bool:
        """
        check if the vault exists
        """
        return self.vault_file.exists() and self.salt_file.exists()



    def create_vault(self, master_pass: str) -> tuple[bool, str]:
        """
        Create a new vault with master password
        Salt = random extra bytes added to a password or secret before deriving a key
        """

        try:
            if len(master_pass) < 8:
                return False, "Password must be at least 8 characters long"

            generate_salt = secrets.token_bytes(32)
            with open(self.salt_file, 'wb') as f:
                f.write(generate_salt)

            key = self.derive_key(master_pass, generate_salt)
            self.fernet = Fernet(key)

            self.passwords = {}
            self.save_vault()
            return True, "Vault created successfully"

        except Exception as e:
            return False, f"Failed to create Vault: {e}"




    def unlock_vault(self, master_pass: str) -> tuple[bool, str]:
        """ Get back the salt -> open the encrypted file
        -> AND decode from bytes to text to get the data

        Key devriation will be done as well here which will be generate from
        the same salt and password again to be used for decryption
        """

        try:
            with open(self.salt_file, 'rb') as f:
                salt = f.read()

            key = self.derive_key(master_pass, salt)
            self.fernet = Fernet(key)

            with open(self.vault_file, 'rb') as f:
                encrypted_data = f.read()

            decrypt = self.fernet.decrypt(encrypted_data)
            decode_data =  json.loads(decrypt.decode())
            return True, "Vault unlocked successfully"
        except Exception as e:
            return False, f"Incorrect password"





    def save_vault(self):
        """"""
        data = json.dumps(self.passwords, indent=2)
        encrypted_data = self.fernet.encrypt(data.encode())

        with open(self.vault_file, 'wb') as f:
            f.write(encrypted_data)






    def add_password(self, service:str, username:str, password:str, notes:str = ""):
        """we load the categories of the added password within the service"""
        self.passwords[service] = {
            "username": username,
            "password": password,
            "notes": notes,
        }
        self.save_vault()




    def delete_password(self, service:str) -> bool:
        """will delete and save to the vault"""
        if service in self.passwords:
            del self.passwords[service]
            self.save_vault()
            return True
        return False




    def get_password(self, service:str) -> dict:
        """Get a password entry"""
        return self.passwords.get(service, None)




    def get_all_services(self) -> list:
        """Get list of all service names"""
        return sorted(self.passwords.keys())





    def generate_password(self, length:int = 16) -> str:
        """Generate a strong random password"""
        random = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
        password = ''.join(secrets.choice(random) for _ in range(length))
        return password























