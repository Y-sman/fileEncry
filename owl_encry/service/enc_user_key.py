# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import Optional

from owl_common.exception import ServiceException
from owl_encry.domain.entity import EncUserKey
from owl_encry.mapper.enc_user_key import EncUserKeyMapper
from owl_encry.service.crypto_service import CryptoService
from owl_common.utils import security_util


class EncUserKeyService:
    """用户密钥服务"""

    @classmethod
    def select_by_user_id(cls, user_id: int) -> Optional[EncUserKey]:
        """根据用户ID查询密钥（密钥与用户一一对应，仅本人可访问）"""
        return EncUserKeyMapper.select_by_user_id(user_id)

    @classmethod
    def generate_key(cls, user_id: int, key_size: int = 2048) -> EncUserKey:
        """
        为用户生成RSA密钥对

        Args:
            user_id: 用户ID
            key_size: 密钥长度

        Returns:
            密钥实体
        """
        existing = EncUserKeyMapper.select_by_user_id(user_id)
        if existing:
            raise ServiceException("用户已存在密钥，请先删除或导出后再生成")

        public_pem, private_pem = CryptoService.generate_rsa_keypair(key_size)
        # 私钥使用用户密码加密存储（简化处理：使用系统密钥加密，实际可用用户密码）
        # 此处为简化，直接存储Base64编码（生产环境应使用更强的加密）
        import base64
        private_enc = base64.b64encode(private_pem.encode()).decode()

        key = EncUserKey(
            user_id=user_id,
            public_key=public_pem,
            private_key_enc=private_enc,
            key_size=key_size,
            status='0',
            create_by=security_util.get_username(),
            remark=''
        )
        from datetime import datetime
        key.create_time = datetime.now()
        EncUserKeyMapper.insert(key)
        key = EncUserKeyMapper.select_by_user_id(user_id)
        return key

    @classmethod
    def export_public_key(cls, user_id: int) -> str:
        """导出用户公钥"""
        key = EncUserKeyMapper.select_by_user_id(user_id)
        if not key:
            raise ServiceException("用户未生成密钥")
        return key.public_key

    @classmethod
    def export_private_key(cls, user_id: int) -> str:
        """导出用户私钥"""
        key = EncUserKeyMapper.select_by_user_id(user_id)
        if not key:
            raise ServiceException("用户未生成密钥")
        import base64
        return base64.b64decode(key.private_key_enc.encode()).decode()

    @classmethod
    def get_private_key_pem(cls, user_id: int) -> str:
        """获取用户私钥PEM（供内部解密使用）"""
        key = EncUserKeyMapper.select_by_user_id(user_id)
        if not key:
            return None
        import base64
        return base64.b64decode(key.private_key_enc.encode()).decode()

    @classmethod
    def get_public_key_pem(cls, user_id: int) -> Optional[str]:
        """获取用户公钥PEM"""
        key = EncUserKeyMapper.select_by_user_id(user_id)
        return key.public_key if key else None
