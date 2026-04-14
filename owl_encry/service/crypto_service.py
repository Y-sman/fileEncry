# -*- coding: utf-8 -*-
# @Author  : balabala

"""
核心加密服务模块
使用 cryptography 库实现 AES/DES 对称加密和 RSA 非对称加密
"""

import base64
import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key, load_pem_private_key,
    Encoding, PublicFormat, PrivateFormat, NoEncryption
)
from cryptography.hazmat.backends import default_backend


class CryptoService:
    """加密服务类"""

    AES_BLOCK_SIZE = 16
    DES_BLOCK_SIZE = 8
    AES_KEY_SIZES = [128, 192, 256]
    RSA_KEY_SIZES = [2048, 4096]

    @classmethod
    def generate_rsa_keypair(cls, key_size: int = 2048) -> Tuple[str, str]:
        """
        生成RSA密钥对

        Args:
            key_size: 密钥长度 2048 或 4096

        Returns:
            (公钥PEM, 私钥PEM)
        """
        if key_size not in cls.RSA_KEY_SIZES:
            key_size = 2048
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        private_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=NoEncryption()
        ).decode('utf-8')
        public_pem = public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        return public_pem, private_pem

    @classmethod
    def rsa_encrypt(cls, public_key_pem: str, data: bytes) -> str:
        """使用RSA公钥加密数据，返回Base64字符串"""
        public_key = load_pem_public_key(public_key_pem.encode(), backend=default_backend())
        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted).decode('utf-8')

    @classmethod
    def rsa_decrypt(cls, private_key_pem: str, encrypted_b64: str) -> bytes:
        """使用RSA私钥解密Base64加密数据"""
        private_key = load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        encrypted = base64.b64decode(encrypted_b64)
        decrypted = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted

    @classmethod
    def sha256_hash(cls, data: bytes) -> str:
        """计算数据SHA256哈希，返回十六进制字符串"""
        import hashlib
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def _generate_iv(cls, block_size: int) -> bytes:
        """生成随机IV"""
        return os.urandom(block_size)

    @classmethod
    def aes_encrypt(cls, key: bytes, data: bytes, iv: bytes = None) -> Tuple[bytes, bytes]:
        """
        AES加密 (CBC模式)

        Args:
            key: 16/24/32 字节密钥
            data: 待加密数据
            iv: 可选，16字节IV

        Returns:
            (加密数据, IV)
        """
        if iv is None:
            iv = cls._generate_iv(cls.AES_BLOCK_SIZE)
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        # PKCS7 padding
        pad_len = cls.AES_BLOCK_SIZE - (len(data) % cls.AES_BLOCK_SIZE)
        padded = data + bytes([pad_len] * pad_len)
        encrypted = encryptor.update(padded) + encryptor.finalize()
        return encrypted, iv

    @classmethod
    def aes_decrypt(cls, key: bytes, encrypted_data: bytes, iv: bytes) -> bytes:
        """AES-CBC 解密"""
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
        pad_len = decrypted[-1]
        return decrypted[:-pad_len]

    @classmethod
    def aes_encrypt_gcm(cls, key: bytes, data: bytes, nonce: bytes = None) -> Tuple[bytes, bytes]:
        """
        AES-GCM 加密。返回 (密文+tag, nonce)，nonce 12 字节。
        """
        if nonce is None:
            nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        ct = aesgcm.encrypt(nonce, data, None)
        return ct, nonce

    @classmethod
    def aes_decrypt_gcm(cls, key: bytes, encrypted_data: bytes, nonce: bytes) -> bytes:
        """AES-GCM 解密。encrypted_data 为密文+tag（末尾 16 字节为 tag）。"""
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, encrypted_data, None)

    @classmethod
    def aes_encrypt_ecb(cls, key: bytes, data: bytes) -> bytes:
        """AES-ECB 加密，无 IV，返回密文。"""
        cipher = Cipher(
            algorithms.AES(key),
            modes.ECB(),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        pad_len = cls.AES_BLOCK_SIZE - (len(data) % cls.AES_BLOCK_SIZE)
        padded = data + bytes([pad_len] * pad_len)
        return encryptor.update(padded) + encryptor.finalize()

    @classmethod
    def aes_decrypt_ecb(cls, key: bytes, encrypted_data: bytes) -> bytes:
        """AES-ECB 解密。"""
        cipher = Cipher(
            algorithms.AES(key),
            modes.ECB(),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
        pad_len = decrypted[-1]
        return decrypted[:-pad_len]

    @classmethod
    def des_encrypt(cls, key: bytes, data: bytes, iv: bytes = None) -> Tuple[bytes, bytes]:
        """
        DES/3DES加密 (CBC模式)

        Args:
            key: 8/16/24字节密钥
            data: 待加密数据
            iv: 可选，8字节IV

        Returns:
            (加密数据, IV)
        """
        if iv is None:
            iv = cls._generate_iv(cls.DES_BLOCK_SIZE)
        # TripleDES 需要 24 字节密钥
        des_key = key[:24] if len(key) >= 24 else (key[:8] * 3)[:24]
        cipher = Cipher(
            algorithms.TripleDES(des_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        pad_len = cls.DES_BLOCK_SIZE - (len(data) % cls.DES_BLOCK_SIZE)
        padded = data + bytes([pad_len] * pad_len)
        encrypted = encryptor.update(padded) + encryptor.finalize()
        return encrypted, iv

    @classmethod
    def des_decrypt(cls, key: bytes, encrypted_data: bytes, iv: bytes) -> bytes:
        """DES/3DES解密"""
        des_key = key[:24] if len(key) >= 24 else (key[:8] * 3)[:24]
        cipher = Cipher(
            algorithms.TripleDES(des_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
        pad_len = decrypted[-1]
        return decrypted[:-pad_len]
