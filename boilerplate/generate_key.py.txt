from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
symmetric_key = Fernet.generate_key()
with open("symmetric_key.key", "wb") as key_file:
    key_file.write(symmetric_key)
