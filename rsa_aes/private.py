import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# RSA私钥
RSA_PRIVATE_KEY_PEM = '''
-----BEGIN RSA PRIVATE KEY-----
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
xVN2XVbI8Bzq2g==
-----END RSA PRIVATE KEY-----
'''


class Private:
    def __init__(self):
        self.backend = default_backend()

        # AES 128
        self.aes_key = None
        self.aes_block_length = 16
        self.aes_encrypt_b64_key = ''

        # RSA with OAEP padding (private key)
        self.rsa_private_key = serialization.load_pem_private_key(RSA_PRIVATE_KEY_PEM.encode(), None, self.backend)

    def get_aes_key(self, encrypt_b64_key):
        """
        解析base64编码, 并使用RSA解密
        """

        if encrypt_b64_key == self.aes_encrypt_b64_key:
            return True

        # base64 decode
        cipher = base64.b64decode(encrypt_b64_key)

        # decrypt
        plain = self.rsa_private_key.decrypt(
            cipher,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # aes key, iv
        key = plain[:32]
        iv = plain[32:]
        self.aes_key = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)

        return False

    def aes_encrypt(self, utf8_text):
        """
        将UTF-8编码的文本AES 128加密之后编码成base64
        """

        enc = self.aes_key.encryptor()

        # encode utf-8 text to bytes
        u8 = utf8_text.encode('utf-8')

        # padding (PKCS7, RFC 5652)
        mod = len(u8) % self.aes_block_length
        count = self.aes_block_length - mod
        u8 += (chr(count) * count).encode()

        # encrypt
        cipher = enc.update(u8) + enc.finalize()

        # base64 encode
        return base64.b64encode(cipher).decode()

    def aes_decrypt(self, encrypted_b64_text):
        """
        将AES 128加密并base64编码过的UTF-8文本解密
        """

        # base64 decode
        cipher = base64.b64decode(encrypted_b64_text)

        # decrypt
        dec = self.aes_key.decryptor()
        plain = dec.update(cipher) + dec.finalize()

        # remove padding, decode to utf-8 text
        count = plain[-1]
        return plain[:-count].decode('utf-8') if count <= len(plain) else None
