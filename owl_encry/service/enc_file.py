# -*- coding: utf-8 -*-
# @Author  : balabala

import os
import uuid
from datetime import datetime
from typing import List, Optional, BinaryIO

from werkzeug.datastructures import FileStorage

from owl_common.config import OWLConfig
from owl_common.exception import ServiceException
from owl_common.utils import security_util
from owl_encry.domain.entity import EncFile
from owl_encry.mapper.enc_file import EncFileMapper
from owl_encry.service.crypto_service import CryptoService
from owl_encry.service.enc_user_key import EncUserKeyService


class EncFileService:
    """加密文件服务"""

    @classmethod
    def _get_encry_path(cls) -> str:
        """获取加密文件存储路径"""
        config = OWLConfig()
        # 使用相对路径替代绝对路径，避免权限问题
        path = os.path.join('uploads', 'encry')
        # 确保路径是绝对路径
        path = os.path.abspath(path)
        # 确保目录存在
        os.makedirs(path, exist_ok=True)
        print(f"Encry path: {path}")
        return path

    @classmethod
    def select_list(cls, query: EncFile) -> List[EncFile]:
        """查询文件列表（仅返回当前用户自己的文件，强制按当前用户过滤）"""
        query.user_id = security_util.get_user_id()
        return EncFileMapper.select_list(query)

    @classmethod
    def get_user_stats(cls, user_id: int) -> dict:
        """个人中心使用统计：文件数量、存储空间（字节）"""
        return {
            "fileCount": EncFileMapper.count_by_user_id(user_id),
            "storageUsed": EncFileMapper.sum_storage_by_user_id(user_id),
        }

    @classmethod
    def select_by_id(cls, file_id: int, user_id: int = None) -> Optional[EncFile]:
        """根据ID查询文件"""
        if user_id:
            return EncFileMapper.select_by_id_and_user(file_id, user_id)
        return EncFileMapper.select_by_id(file_id)

    @classmethod
    def _normalize_sym_key(cls, raw: str, algo: str) -> bytes:
        """将用户输入的密钥转为 bytes：支持十六进制或 UTF-8。AES 需 16/24/32 字节，DES 需 8 或 24 字节。"""
        try:
            raw = (raw or '').strip()
            if not raw:
                return None
            if all(c in '0123456789abcdefABCDEF' for c in raw.replace(' ', '')):
                key = bytes.fromhex(raw.replace(' ', ''))
            else:
                key = raw.encode('utf-8')
            if algo.upper() == 'AES':
                if len(key) not in (16, 24, 32):
                    if len(key) < 16:
                        key = (key + b'\0' * 32)[:16]
                    elif len(key) < 24:
                        key = (key + b'\0' * 32)[:24]
                    else:
                        key = (key + b'\0' * 32)[:32]
            elif algo.upper() == 'DES':
                if len(key) < 8:
                    key = (key + b'\0' * 8)[:8]
                elif len(key) < 24:
                    key = (key + b'\0' * 24)[:24]
                else:
                    key = key[:24]
            return key
        except Exception:
            return None

    @classmethod
    def upload_encrypt(
        cls,
        file: FileStorage,
        encrypt_algo: str = 'AES',
        aes_mode: str = 'CBC',
        user_sym_key: str = None,
    ) -> EncFile:
        """
        加密上传文件。

        Args:
            file: 文件对象
            encrypt_algo: 对称加密算法 AES 或 DES
            aes_mode: AES 模式，仅当 encrypt_algo 为 AES 时有效：CBC、GCM、ECB
            user_sym_key: 用户提供的对称密钥（可选，十六进制或字符串），为空则随机生成

        Returns:
            加密文件实体
        """
        import base64
        user_id = security_util.get_user_id()
        public_key = EncUserKeyService.get_public_key_pem(user_id)
        if not public_key:
            raise ServiceException("请先生成RSA密钥对")

        data = file.read()
        file_hash = CryptoService.sha256_hash(data)

        algo_upper = encrypt_algo.upper()
        mode_upper = (aes_mode or 'CBC').upper()

        if user_sym_key:
            sym_key = cls._normalize_sym_key(user_sym_key, algo_upper)
            if not sym_key:
                raise ServiceException("无效的密钥格式，请使用十六进制或字符串")
        else:
            if algo_upper == 'AES':
                sym_key = os.urandom(32)
            else:
                sym_key = os.urandom(24)

        if algo_upper == 'AES':
            if mode_upper == 'GCM':
                encrypted_data, iv = CryptoService.aes_encrypt_gcm(sym_key, data)
                iv_b64 = base64.b64encode(iv).decode()
                algo_stored = 'AES-GCM'
            elif mode_upper == 'ECB':
                encrypted_data = CryptoService.aes_encrypt_ecb(sym_key, data)
                iv_b64 = ''
                algo_stored = 'AES-ECB'
            else:
                encrypted_data, iv = CryptoService.aes_encrypt(sym_key, data)
                iv_b64 = base64.b64encode(iv).decode()
                algo_stored = 'AES-CBC'
        elif algo_upper == 'DES':
            encrypted_data, iv = CryptoService.des_encrypt(sym_key, data)
            iv_b64 = base64.b64encode(iv).decode()
            algo_stored = 'DES'
        else:
            raise ServiceException("不支持的加密算法，请使用 AES 或 DES")

        sym_key_enc = CryptoService.rsa_encrypt(public_key, sym_key)

        base_path = cls._get_encry_path()
        date_dir = datetime.now().strftime('%Y%m%d')
        # 确保文件名安全
        safe_filename = os.path.basename(file.filename)
        stored_name = str(uuid.uuid4()).replace('-', '') + '_' + os.path.splitext(safe_filename)[1]
        rel_path = os.path.join(date_dir, stored_name)
        full_path = os.path.join(base_path, rel_path)
        # 确保使用统一的路径分隔符
        full_path = os.path.normpath(full_path)
        
        # 确保目录存在
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")
        
        # 确保目录可写
        if not os.access(dir_path, os.W_OK):
            raise ServiceException(f"Directory not writable: {dir_path}")
        
        # 写入文件
        with open(full_path, 'wb') as f:
            f.write(encrypted_data)
        print(f"File written successfully: {full_path}")

        enc_file = EncFile(
            user_id=user_id,
            original_name=file.filename,
            stored_name=stored_name,
            file_path=rel_path.replace('\\', '/'),
            file_size=len(encrypted_data),
            encrypt_algo=algo_stored,
            sym_key_enc=sym_key_enc,
            iv=iv_b64,
            file_hash=file_hash,
            del_flag='0',
            create_by=security_util.get_username(),
            create_time=datetime.now(),
            remark=''
        )
        file_id = EncFileMapper.insert(enc_file)
        return EncFileMapper.select_by_id(file_id) or enc_file

    @classmethod
    def decrypt_download(cls, file_id: int, user_id: int = None, verify_hash: str = None) -> tuple[bytes, str]:
        """
        解密下载文件，可选哈希校验

        Args:
            file_id: 文件ID
            user_id: 用户ID（可选）
            verify_hash: 用于校验的哈希值（可选），若提供则解密后比对

        Returns:
            (文件字节数据, 原始文件名)
        """
        user_id = user_id or security_util.get_user_id()
        enc_file = EncFileMapper.select_by_id_and_user(file_id, user_id)
        if not enc_file:
            raise ServiceException("文件不存在或无权访问")

        private_key = EncUserKeyService.get_private_key_pem(user_id)
        if not private_key:
            raise ServiceException("无法获取解密密钥")

        base_path = cls._get_encry_path()
        full_path = os.path.join(base_path, enc_file.file_path.replace('/', os.sep))
        if not os.path.exists(full_path):
            raise ServiceException("文件已丢失")

        with open(full_path, 'rb') as f:
            encrypted_data = f.read()

        import base64
        algo = (enc_file.encrypt_algo or '').upper()
        iv_b64 = (enc_file.iv or '').strip()
        iv = base64.b64decode(iv_b64) if iv_b64 else b''
        sym_key = CryptoService.rsa_decrypt(private_key, enc_file.sym_key_enc)

        if algo == 'AES-GCM':
            decrypted = CryptoService.aes_decrypt_gcm(sym_key, encrypted_data, iv)
        elif algo == 'AES-ECB':
            decrypted = CryptoService.aes_decrypt_ecb(sym_key, encrypted_data)
        elif algo == 'AES-CBC' or algo == 'AES':
            decrypted = CryptoService.aes_decrypt(sym_key, encrypted_data, iv)
        elif algo == 'DES':
            decrypted = CryptoService.des_decrypt(sym_key, encrypted_data, iv)
        else:
            raise ServiceException("不支持的加密算法或格式")

        # 哈希校验：优先使用用户提供的 verify_hash，否则使用存储的 file_hash
        expected_hash = verify_hash or (enc_file.file_hash if enc_file.file_hash else None)
        if expected_hash:
            actual_hash = CryptoService.sha256_hash(decrypted)
            expected_hash = expected_hash.strip().lower()
            actual_hash = actual_hash.lower()
            if expected_hash != actual_hash:
                raise ServiceException(
                    f"文件完整性校验失败！期望哈希: {expected_hash[:16]}...，实际哈希: {actual_hash[:16]}..."
                )

        return decrypted, enc_file.original_name

    @classmethod
    def delete_file(cls, file_id: int, user_id: int = None) -> int:
        """删除文件（逻辑删除）"""
        user_id = user_id or security_util.get_user_id()
        enc_file = EncFileMapper.select_by_id_and_user(file_id, user_id)
        if not enc_file:
            raise ServiceException("文件不存在或无权访问")
        return EncFileMapper.delete_by_id(file_id)

    @classmethod
    def delete_files(cls, file_ids: List[int], user_id: int = None) -> int:
        """批量删除"""
        user_id = user_id or security_util.get_user_id()
        for fid in file_ids:
            enc_file = EncFileMapper.select_by_id_and_user(fid, user_id)
            if enc_file:
                EncFileMapper.delete_by_id(fid)
        return len(file_ids)

    @classmethod
    def share_file_to_user(cls, file_id: int, target_user_id: int) -> int:
        """
        分享文件给指定用户

        Args:
            file_id: 文件ID
            target_user_id: 目标用户ID

        Returns:
            分享ID

        Raises:
            ServiceException: 文件不存在、用户无密钥等异常
        """
        print(f"分享文件: file_id={file_id}, target_user_id={target_user_id}")
        
        # 1. 获取当前用户ID
        current_user_id = security_util.get_user_id()
        
        # 2. 获取文件记录
        enc_file = cls.select_by_id(file_id, current_user_id)
        if not enc_file:
            raise ServiceException("文件不存在或无权访问")
        
        # 3. 获取当前用户私钥
        private_key = EncUserKeyService.get_private_key_pem(current_user_id)
        if not private_key:
            raise ServiceException("无法获取当前用户私钥")
        print("获取当前用户私钥成功")
        
        # 4. 解密文件的 sym_key_enc 得到原始AES密钥
        try:
            aes_key = CryptoService.rsa_decrypt(private_key, enc_file.sym_key_enc)
            print(f"解密原AES密钥成功, 长度: {len(aes_key)}")
        except Exception as e:
            raise ServiceException(f"解密密钥失败: {str(e)}")
        
        # 5. 获取目标用户公钥
        target_public_key = EncUserKeyService.get_public_key_pem(target_user_id)
        if not target_public_key:
            raise ServiceException("目标用户未生成RSA密钥对")
        
        # 6. 用目标用户公钥重新加密AES密钥
        try:
            new_sym_key_enc = CryptoService.rsa_encrypt(target_public_key, aes_key)
            print("加密新AES密钥成功")
        except Exception as e:
            raise ServiceException(f"加密密钥失败: {str(e)}")
        
        # 7. 创建 FileShare 实体
        from owl_encry.domain.entity import FileShare
        from owl_encry.domain.po import FileSharePo
        from owl_encry.mapper.file_share import FileShareMapper
        
        share = FileSharePo(
            file_id=file_id,
            owner_id=current_user_id,
            target_user_id=target_user_id,
            sym_key_enc=new_sym_key_enc,
            status=0,
            share_from_chat=1  # 从聊天分享
        )
        
        # 8. 保存分享记录
        try:
            share_id = FileShareMapper.insert(share)
            print(f"分享记录插入成功, share_id: {share_id}")
            return share_id
        except Exception as e:
            raise ServiceException(f"保存分享记录失败: {str(e)}")

    @classmethod
    def upload_for_share(cls, file: object, receiver_id: int) -> dict:
        """
        为分享而加密上传文件

        Args:
            file: 文件对象
            receiver_id: 接收者用户ID

        Returns:
            包含分享信息的字典

        Raises:
            ServiceException: 接收者无密钥等异常
        """
        import base64
        
        # 1. 获取当前用户ID
        current_user_id = security_util.get_user_id()
        
        # 2. 获取接收者公钥
        receiver_public_key = EncUserKeyService.get_public_key_pem(receiver_id)
        if not receiver_public_key:
            raise ServiceException("接收者未生成RSA密钥对")
        
        # 3. 读取文件数据
        data = file.read()
        file_hash = CryptoService.sha256_hash(data)
        
        # 4. 生成AES密钥
        sym_key = os.urandom(32)  # 256位AES密钥
        
        # 5. 加密文件
        encrypted_data, iv = CryptoService.aes_encrypt(sym_key, data)
        iv_b64 = base64.b64encode(iv).decode()
        
        # 6. 用接收者公钥加密AES密钥
        sym_key_enc = CryptoService.rsa_encrypt(receiver_public_key, sym_key)
        
        # 7. 保存加密文件
        base_path = cls._get_encry_path()
        date_dir = datetime.now().strftime('%Y%m%d')
        safe_filename = os.path.basename(file.filename)
        stored_name = str(uuid.uuid4()).replace('-', '') + '_' + os.path.splitext(safe_filename)[1]
        rel_path = os.path.join(date_dir, stored_name)
        full_path = os.path.join(base_path, rel_path)
        full_path = os.path.normpath(full_path)
        
        # 确保目录存在
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        # 写入文件
        with open(full_path, 'wb') as f:
            f.write(encrypted_data)
        
        # 8. 创建文件记录
        enc_file = EncFile(
            user_id=current_user_id,
            original_name=file.filename,
            stored_name=stored_name,
            file_path=rel_path.replace('\\', '/'),
            file_size=len(encrypted_data),
            encrypt_algo='AES-CBC',
            sym_key_enc=sym_key_enc,
            iv=iv_b64,
            file_hash=file_hash,
            del_flag='0',
            create_by=security_util.get_username(),
            create_time=datetime.now(),
            remark='分享文件'
        )
        file_id = EncFileMapper.insert(enc_file)
        
        # 9. 创建分享记录
        from owl_encry.domain.po import FileSharePo
        from owl_encry.mapper.file_share import FileShareMapper
        
        share = FileSharePo(
            file_id=file_id,
            owner_id=current_user_id,
            target_user_id=receiver_id,
            sym_key_enc=sym_key_enc,
            status=0,
            share_from_chat=1  # 从聊天分享
        )
        
        share_id = FileShareMapper.insert(share)
        
        return {
            'file_id': file_id,
            'share_id': share_id,
            'file_name': file.filename,
            'file_size': len(data)
        }
