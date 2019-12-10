import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
backend = default_backend()

def initVector(key):
    data = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
    encryptor = cipher.encryptor()

    iVector = encryptor.update(data) + encryptor.finalize()
    return iVector

def generateKey():
    while True:
        data = os.urandom(32)
        salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=16,
            salt=salt,
            iterations=100000,
            backend=backend
        )

        key = kdf.derive(data)
        vi = initVector(key)
        keys = key+b'.'+vi
        if test(keys):
            break
    return keys

def test(keys):
    try:
        cripted_text = encrypt(keys, b'An encryption test')
        return True
    except ValueError:
        return False
            

def pad(unpadded_data):
    padder = PKCS7(128).padder()
    padded_data = padder.update(unpadded_data) + padder.finalize()
    return padded_data

def unpad(padded_data):
    unpadder = PKCS7(128).unpadder()
    unppaded_data = unpadder.update(padded_data) + unpadder.finalize()
    return unppaded_data

def encrypt(key, unpadded_data):
    keys = key.split(b'.')
    key = keys[0] #key
    vi = keys[1] #vector

    cipher = Cipher(algorithms.AES(key), modes.CBC(vi), backend=backend)
    encryptor = cipher.encryptor()
    padded_data = pad(unpadded_data)
    crypted = encryptor.update(padded_data) + encryptor.finalize()
    return crypted

def decrypt(key, padded_data):
    keys = key.split(b'.')
    key = keys[0] #key
    vi = keys[1] #vector

    cipher = Cipher(algorithms.AES(key), modes.CBC(vi), backend=backend)
    decryptor = cipher.decryptor()
    padded_plain = decryptor.update(padded_data) + decryptor.finalize()
    plain = unpad(padded_plain)
    return plain


