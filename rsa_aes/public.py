import base64
import hashlib
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# 加盐
SALT = b'6f074cac66b711eba5b0d0c6372bb8ad'

# RSA公钥
RSA_PUBLIC_KEY_PEM = '''
-----BEGIN RSA PUBLIC KEY-----
MIICCgKCAgEAv1NvVXpaLO0wedsL8fhc8osSkzBZK4OLSjLOKU8THHAQdVc0JkSr
1TWVGyLjHlRBTPWTrdsUgFcSjneK0EyQgHH4S/PuQW7uOX2mEiw3mH5HZOWUrGeF
sW9jJhdDamCOsx5W5UbhHBlyjt6sb7HoE2KI/t+UeCiviz/7Qpr833cWJ6v6Mv5b
qDfPfp6cmYElloCYKlWnRjL9J16HW/4f1UwSMfCW4FMDPY4pj0Tojf3O3r6/h6FL
xdRmhahzXjFty/0M7AWIMi4kvR9OzjOf5lgwpq2s5t8wgkRDWLWOZ8ra7nEtzUhx
s0lcI5HeK0RYvb8ousPKn4LymCK2a+l+ZczNUTmkuZKzTDPbWQ+wyhJj1DsSmezI
tr+zd9qcQcYk3xJq/7m02ca7AGVHK8CuVxTIWwEjECH31/TozVQbNCL/xg+1Vfxn
FNyFXF6meyDG/tG7Fani+sy8PUMys0jOol4HrD5ErOwBxIJvjHpEIwWO0UmFihcz
o1w1v+RjILbYSjan21udFdinPHIAbdHS5p11TXpUReroLakUz3S7P7B6Bkwj1eUZ
rjoVtxdIeKFXfC1yAG8P9jlmPQnlJnbH2eYHJMW4HQyyh1zVKodi4uWFXpJdzAQa
2w2tMcrrznkcl8rh+QZupaHOHtcLOi9DJcpnd1nCyxqFmjtIoM5D9p8CAwEAAQ==
-----END RSA PUBLIC KEY-----
'''


class Public:
    def __init__(self):
        self.backend = default_backend()

        # AES 128
        self.aes_key = None
        self.aes_block_length = 16

        # RSA with OAEP padding (public key)
        self.rsa_public_key = serialization.load_pem_public_key(RSA_PUBLIC_KEY_PEM.encode(), self.backend)

    def gen_aes_keys(self):
        """
        随机生成AES 128 KEY & SIGN
        使用RSA公钥加密, base64编码, sha1加盐加签

        key: 32, iv: 16
          |
        rsa encrypt with public key
          |
        base64, sha1
        """

        # random key, iv
        key = os.urandom(32)
        iv = os.urandom(16)
        self.aes_key = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)

        # encrypt
        cipher = self.rsa_public_key.encrypt(
            key + iv,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # base64 encode, sha1
        return base64.b64encode(cipher).decode(), hashlib.sha1(cipher).hexdigest()

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
