# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import Dict, Any, Tuple
import logging
import os

from owl_common.utils import security_util
from owl_common.exception import ServiceException
from owl_encry.domain.po import FileSharePo
from owl_encry.mapper.file_share import FileShareMapper
from owl_encry.mapper.enc_file import EncFileMapper
from owl_encry.service.enc_user_key import EncUserKeyService
from owl_encry.service.crypto_service import CryptoService
from owl_encry.service.enc_file import EncFileService
from owl_system.mapper.sys_user import SysUserMapper

# 配置日志
logger = logging.getLogger(__name__)


class FileShareService:
    """文件分享服务"""

    @staticmethod
    def _decrypt_shared_record(share: FileSharePo) -> Tuple[bytes, str]:
        """按分享记录解密文件，并执行完整性校验。"""
        current_user_id = security_util.get_user_id()

        private_key = EncUserKeyService.get_private_key_pem(current_user_id)
        if not private_key:
            logger.warning(f"无法获取解密密钥: user_id={current_user_id}")
            raise ServiceException("无法获取解密密钥")

        try:
            aes_key = CryptoService.rsa_decrypt(private_key, share.sym_key_enc)
            logger.info(f"解密密钥成功: key_length={len(aes_key)} bytes")
        except Exception as exc:
            logger.error(f"解密密钥失败: {str(exc)}")
            raise ServiceException(f"解密密钥失败: {str(exc)}")

        enc_file = EncFileMapper.select_by_id(share.file_id)
        if not enc_file:
            logger.warning(f"文件不存在: file_id={share.file_id}")
            raise ServiceException("文件不存在")

        base_path = EncFileService._get_encry_path()
        full_path = os.path.join(base_path, enc_file.file_path.replace('/', os.sep))
        if not os.path.exists(full_path):
            logger.warning(f"文件已丢失: {full_path}")
            raise ServiceException("文件已丢失")

        with open(full_path, 'rb') as f:
            encrypted_data = f.read()

        import base64
        algo = (enc_file.encrypt_algo or '').upper()
        iv_b64 = (enc_file.iv or '').strip()
        iv = base64.b64decode(iv_b64) if iv_b64 else b''

        if algo == 'AES-GCM':
            decrypted_data = CryptoService.aes_decrypt_gcm(aes_key, encrypted_data, iv)
        elif algo == 'AES-ECB':
            decrypted_data = CryptoService.aes_decrypt_ecb(aes_key, encrypted_data)
        elif algo in ('AES-CBC', 'AES'):
            decrypted_data = CryptoService.aes_decrypt(aes_key, encrypted_data, iv)
        elif algo == 'DES':
            decrypted_data = CryptoService.des_decrypt(aes_key, encrypted_data, iv)
        else:
            raise ServiceException("不支持的加密算法或格式")

        expected_hash = (enc_file.file_hash or '').strip().lower()
        if expected_hash:
            actual_hash = CryptoService.sha256_hash(decrypted_data).lower()
            if actual_hash != expected_hash:
                raise ServiceException("文件完整性校验失败，文件可能已损坏或被篡改")

        logger.info(f"文件解密成功: file_name={enc_file.original_name}, size={len(decrypted_data)} bytes")
        return decrypted_data, enc_file.original_name

    @staticmethod
    def get_shared_to_me(page: int, page_size: int) -> Dict[str, Any]:
        """获取分享给我的文件列表。"""
        current_user_id = security_util.get_user_id()
        logger.info(f"获取分享给我的文件列表: user_id={current_user_id}, page={page}, page_size={page_size}")

        shares = FileShareMapper.select_by_target(current_user_id)
        logger.info(f"查询到 {len(shares)} 条分享记录")

        result = []
        for share in shares:
            file = EncFileMapper.select_by_id(share.file_id)
            if not file:
                logger.warning(f"文件不存在: file_id={share.file_id}")
                continue

            owner = SysUserMapper.select_user_by_id(share.owner_id)
            owner_name = owner.nick_name if owner else ''

            result.append({
                'share_id': share.share_id,
                'file_id': share.file_id,
                'file_name': file.original_name,
                'file_size': file.file_size,
                'owner_id': share.owner_id,
                'owner_name': owner_name,
                'create_time': share.create_time
            })

        total = len(result)
        start = (page - 1) * page_size
        end = start + page_size
        rows = result[start:end]

        logger.info(f"获取分享给我的文件列表完成: total={total}, return_rows={len(rows)}")
        return {
            'total': total,
            'rows': rows
        }

    @staticmethod
    def get_shared_by_me(page: int, page_size: int) -> Dict[str, Any]:
        """获取我分享的文件列表。"""
        current_user_id = security_util.get_user_id()
        logger.info(f"获取我分享的文件列表: user_id={current_user_id}, page={page}, page_size={page_size}")

        shares = FileShareMapper.select_by_owner(current_user_id)
        logger.info(f"查询到 {len(shares)} 条分享记录")

        result = []
        for share in shares:
            file = EncFileMapper.select_by_id(share.file_id)
            if not file:
                logger.warning(f"文件不存在: file_id={share.file_id}")
                continue

            target_user = SysUserMapper.select_user_by_id(share.target_user_id)
            target_user_name = target_user.nick_name if target_user else ''

            result.append({
                'share_id': share.share_id,
                'file_id': share.file_id,
                'file_name': file.original_name,
                'file_size': file.file_size,
                'target_user_id': share.target_user_id,
                'target_user_name': target_user_name,
                'status': share.status,
                'create_time': share.create_time
            })

        total = len(result)
        start = (page - 1) * page_size
        end = start + page_size
        rows = result[start:end]

        logger.info(f"获取我分享的文件列表完成: total={total}, return_rows={len(rows)}")
        return {
            'total': total,
            'rows': rows
        }

    @staticmethod
    def revoke_share(share_id: int) -> bool:
        """撤销分享。"""
        current_user_id = security_util.get_user_id()
        logger.info(f"撤销分享: share_id={share_id}, user_id={current_user_id}")

        share = FileShareMapper.select_by_id(share_id)
        if not share:
            logger.warning(f"分享记录不存在或已撤销: share_id={share_id}")
            raise ServiceException("分享记录不存在或已撤销")

        if share.owner_id != current_user_id:
            logger.warning(
                f"无权限撤销此分享: share_id={share_id}, owner_id={share.owner_id}, user_id={current_user_id}"
            )
            raise ServiceException("无权限撤销此分享")

        FileShareMapper.update_status(share_id, 1)
        logger.info(f"撤销分享成功: share_id={share_id}")
        return True

    @staticmethod
    def download_shared_file(share_id: int) -> Tuple[bytes, str]:
        """下载分享文件。"""
        current_user_id = security_util.get_user_id()
        logger.info(f"下载分享文件: share_id={share_id}, user_id={current_user_id}")

        share = FileShareMapper.select_by_id(share_id)
        if not share:
            logger.warning(f"分享记录不存在或已撤销: share_id={share_id}")
            raise ServiceException("分享记录不存在或已撤销")

        if share.target_user_id != current_user_id:
            logger.warning(
                f"无权限下载此文件: share_id={share_id}, target_user_id={share.target_user_id}, user_id={current_user_id}"
            )
            raise ServiceException("无权限下载此文件")

        return FileShareService._decrypt_shared_record(share)

    @staticmethod
    def download_shared_file_by_file_id(file_id: int) -> Tuple[bytes, str]:
        """通过聊天消息中的 file_id 下载当前用户收到的分享文件。"""
        current_user_id = security_util.get_user_id()
        logger.info(f"按 file_id 下载分享文件: file_id={file_id}, user_id={current_user_id}")

        share = FileShareMapper.select_by_file_and_target(file_id, current_user_id)
        if not share:
            logger.warning(f"未找到可用的分享记录: file_id={file_id}, user_id={current_user_id}")
            raise ServiceException("未找到可用的文件分享记录")

        return FileShareService._decrypt_shared_record(share)
