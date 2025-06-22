from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
from sympy import randprime
# ---------------------- RSA Encryption Class ----------------------
class RSAEncryption:
    def __init__(self):
        self._key = RSA.generate(2048)  # Generate RSA key
        self._private_key = self._key.export_key()
        self.public_key = self._key.publickey().export_key()

    @property
    def private_key(self):
        """Getter for private key"""
        return self._private_key

    @private_key.setter
    def private_key(self, new_key):
        """Setter for private key - Updates RSA key pair"""
        try:
            self._key = RSA.import_key(new_key)
            self._private_key = new_key
            self.public_key = self._key.publickey().export_key()  # Update public key as well
        except ValueError:
            raise ValueError("Invalid RSA Private Key!")

    def encrypt(self, public_key, message):
        recipient_key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(recipient_key)
        return cipher.encrypt(message)

    def decrypt(self, ciphertext,key):
        cipher = PKCS1_OAEP.new(RSA.import_key(key))
        return cipher.decrypt(ciphertext)

    def decrypt_key(self, cipher_text):
        """Decrypts an encrypted key to retrieve the original key."""
        return self.decrypt(cipher_text).decode()

# ---------------------- Diffie-Hellman Key Exchange Class ----------------------
class DiffieHellman:
    def __init__(self, p, g):
        self.p = p
        self.g = g
        self.private_key = random.randint(2, p - 2)
        self.public_key = pow(g, self.private_key, p)

    def compute_shared_secret(self, received_public_key):
        return pow(received_public_key, self.private_key, self.p)
