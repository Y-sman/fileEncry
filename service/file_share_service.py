# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging
import os

# 配置日志
logger = logging.getLogger(__name__)

from owl_common.utils import security_util
from owl_common.exception import ServiceException
from owl_encry.domain.po import FileSharePo, EncFilePo
from owl_encry.mapper.file_share import FileShareMapper
from owl_encry.mapper.enc_file import EncFileMapper
from owl_encry.service.enc_user_key import EncUserKeyService
from owl_encry.service.crypto_service import CryptoService
from owl_encry.service.enc_file import EncFileService
from owl_system.mapper.sys_user import SysUserMapper


class FileShareService:
    """文件分享服务"""

    @staticmethod
    def get_shared_to_me(page: int, page_size: int) -> Dict[str, Any]:
        """
        获取分享给我的文件列表
        
        Args:
            page: 页码
            page_size: 每页大小
            
        Returns:
            分页数据，包含 total, rows
        """
        current_user_id = security_util.get_user_id()
        logger.info(f"获取分享给我的文件列表: user_id={current_user_id}, page={page}, page_size={page_size}")
        
        # 查询分享记录
        shares = FileShareMapper.select_by_target(current_user_id)
        logger.info(f"查询到 {len(shares)} 条分享记录")
        
        # 构建结果列表
        result = []
        for share in shares:
            # 获取文件信息
            file = EncFileMapper.select_by_id(share.file_id)
            if not file:
                logger.warning(f"文件不存在: file_id={share.file_id}")
                continue
            
            # 获取分享者信息
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
        
        # 分页处理
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
        """
        获取我分享的文件列表
        
        Args:
            page: 页码
            page_size: 每页大小
            
        Returns:
            分页数据，包含 total, rows
        """
        current_user_id = security_util.get_user_id()
        logger.info(f"获取我分享的文件列表: user_id={current_user_id}, page={page}, page_size={page_size}")
        
        # 查询分享记录
        shares = FileShareMapper.select_by_owner(current_user_id)
        logger.info(f"查询到 {len(shares)} 条分享记录")
        
        # 构建结果列表
        result = []
        for share in shares:
            # 获取文件信息
            file = EncFileMapper.select_by_id(share.file_id)
            if not file:
                logger.warning(f"文件不存在: file_id={share.file_id}")
                continue
            
            # 获取目标用户信息
            target_user = SysUserMapper.select_user_by_id(share.target_user_id)
            target_user_name = target_user.nick_name if target_user else ''
            
            result.append({
                'share_id': share.share_id,
                'file_id': share.file_id,
                'file_name': file.original_name,
                'target_user_id': share.target_user_id,
                'target_user_name': target_user_name,
                'status': share.status,
                'create_time': share.create_time
            })
        
        # 分页处理
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
        """
        撤销分享
        
        Args:
            share_id: 分享ID
            
        Returns:
            是否成功
        """
        current_user_id = security_util.get_user_id()
        logger.info(f"撤销分享: share_id={share_id}, user_id={current_user_id}")
        
        # 查询分享记录
        share = FileShareMapper.select_by_id(share_id)
        if not share:
            logger.warning(f"分享记录不存在或已撤销: share_id={share_id}")
            raise ServiceException("分享记录不存在或已撤销")
        
        # 验证权限
        if share.owner_id != current_user_id:
            logger.warning(f"无权限撤销此分享: share_id={share_id}, owner_id={share.owner_id}, user_id={current_user_id}")
            raise ServiceException("无权限撤销此分享")
        
        # 更新状态为已撤销
        FileShareMapper.update_status(share_id, 1)
        logger.info(f"撤销分享成功: share_id={share_id}")
        return True

    @staticmethod
    def download_shared_file(share_id: int) -> Tuple[bytes, str]:
        """
        下载分享的文件
        
        Args:
            share_id: 分享ID
            
        Returns:
            (文件字节数据, 原始文件名)
        """
        current_user_id = security_util.get_user_id()
        logger.info(f"下载分享文件: share_id={share_id}, user_id={current_user_id}")
        
        # 查询分享记录
        share = FileShareMapper.select_by_id(share_id)
        if not share:
            logger.warning(f"分享记录不存在或已撤销: share_id={share_id}")
            raise ServiceException("分享记录不存在或已撤销")
        
        # 验证权限（接收方或管理员可下载）
        from owl_common.utils.security_util import is_admin
        if share.target_user_id != current_user_id and not is_admin(current_user_id):
            logger.warning(f"无权限下载此文件: share_id={share_id}, target_user_id={share.target_user_id}, user_id={current_user_id}")
            raise ServiceException("无权限下载此文件")
        
        # 获取当前用户私钥
        private_key = EncUserKeyService.get_private_key_pem(current_user_id)
        if not private_key:
            logger.warning(f"无法获取解密密钥: user_id={current_user_id}")
            raise ServiceException("无法获取解密密钥")
        
        # 用私钥解密 sym_key_enc 得到原始AES密钥
        try:
            aes_key = CryptoService.rsa_decrypt(private_key, share.sym_key_enc)
            logger.info(f"解密密钥成功: key_length={len(aes_key)} bytes")
        except Exception as e:
            logger.error(f"解密密钥失败: {str(e)}")
            raise ServiceException(f"解密密钥失败: {str(e)}")
        
        # 根据 file_id 查询原文件记录
        enc_file = EncFileMapper.select_by_id(share.file_id)
        if not enc_file:
            logger.warning(f"文件不存在: file_id={share.file_id}")
            raise ServiceException("文件不存在")
        
        # 直接实现解密逻辑，不使用 EncFileService.decrypt_download（避免用户权限检查）
        logger.info(f"开始解密文件: file_id={share.file_id}, file_name={enc_file.original_name}")
        
        # 获取文件存储路径
        base_path = EncFileService._get_encry_path()
        full_path = os.path.join(base_path, enc_file.file_path.replace('/', os.sep))
        if not os.path.exists(full_path):
            logger.warning(f"文件已丢失: {full_path}")
            raise ServiceException("文件已丢失")
        
        # 读取加密文件
        with open(full_path, 'rb') as f:
            encrypted_data = f.read()
        
        # 解密文件
        import base64
        algo = (enc_file.encrypt_algo or '').upper()
        iv_b64 = (enc_file.iv or '').strip()
        iv = base64.b64decode(iv_b64) if iv_b64 else b''
        
        if algo == 'AES-GCM':
            decrypted_data = CryptoService.aes_decrypt_gcm(aes_key, encrypted_data, iv)
        elif algo == 'AES-ECB':
            decrypted_data = CryptoService.aes_decrypt_ecb(aes_key, encrypted_data)
        elif algo == 'AES-CBC' or algo == 'AES':
            decrypted_data = CryptoService.aes_decrypt(aes_key, encrypted_data, iv)
        elif algo == 'DES':
            decrypted_data = CryptoService.des_decrypt(aes_key, encrypted_data, iv)
        else:
            raise ServiceException("不支持的加密算法或格式")
        
        logger.info(f"文件解密成功: file_name={enc_file.original_name}, size={len(decrypted_data)} bytes")
        original_name = enc_file.original_name
        
        return decrypted_data, original_name
