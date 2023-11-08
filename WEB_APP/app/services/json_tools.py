
import cryptography
import json
import base64
from cryptography.hazmat.primitives import serialization

from cryptography.fernet import Fernet

def safe_encode(value):
    
    if isinstance(value, bytes):
        return base64.b64encode(value).decode('utf-8')
    return value

def safe_encode_dict(d):
    
    return {k: safe_encode(v) for k, v in d.items()}

def encrypt_json(data, symmetric_key):
    """
    Encrypts a Python object (list or dictionary) into JSON-formatted string and then encrypts it with a symmetric key.

    :param data: Python object (list or dictionary) to be encrypted.
    :param symmetric_key: Symmetric key used for encryption.
    :return: Encrypted bytes.
    """
    safe_data = [safe_encode_dict(item) if isinstance(item, dict) else safe_encode(item) for item in data]

    # Convert the Python object to a JSON-formatted string
    json_string = json.dumps(safe_data).encode('utf-8')
    cipher_suite = Fernet(symmetric_key)
    encrypted_data = cipher_suite.encrypt(json_string)
    
    return encrypted_data
def decrypt_json(encrypted_data, symmetric_key):
    try:
        cipher_suite = Fernet(symmetric_key)
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode('utf-8'))
    except cryptography.fernet.InvalidToken as e:
        print(f"InvalidToken exception: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
