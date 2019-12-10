from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
backend = default_backend()

def generateKey():
    private = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=backend
    )
    public = private.public_key()

    return private, public

def encrypt(key, plain_msg):
    return key.encrypt(
        plain_msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt(key, cripted_msg):
    return key.decrypt(
        cripted_msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def serialize(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def deserialize(public_bytes):
    return serialization.load_der_public_key(
        data = public_bytes,
        backend=backend
    )


