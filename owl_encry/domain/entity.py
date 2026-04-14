# -*- coding: utf-8 -*-
# @Author  : balabala

from datetime import datetime
from typing import Optional
from pydantic import BeforeValidator, Field
from typing_extensions import Annotated

from owl_common.base.model import AuditEntity, BaseEntity, VoAccess
from owl_common.base.transformer import str_to_int, to_datetime


class EncUserKey(AuditEntity):
    """用户RSA密钥对实体"""

    key_id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(gt=0, default=None, vo=VoAccess(query=True))
    ]
    user_id: Annotated[int, BeforeValidator(str_to_int), Field(gt=0)]
    public_key: Optional[str] = None
    private_key_enc: Optional[str] = None
    key_size: Optional[int] = Field(default=2048)
    status: Annotated[
        Optional[str],
        Field(default='0', vo=VoAccess(query=True))
    ]


class EncFile(AuditEntity):
    """加密文件实体"""

    file_id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(gt=0, default=None, vo=VoAccess(query=True))
    ]
    user_id: Annotated[Optional[int], BeforeValidator(str_to_int), Field(default=None, gt=0)]
    original_name: Annotated[
        Optional[str],
        Field(default=None, vo=VoAccess(query=True))
    ]
    stored_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = Field(default=0)
    encrypt_algo: Optional[str] = Field(default=None)  # 查询时 None 表示不过滤；上传时由表单传入
    sym_key_enc: Optional[str] = None
    iv: Optional[str] = None
    file_hash: Optional[str] = None  # 原始文件SHA256哈希(十六进制)，用于下载时完整性校验
    del_flag: Annotated[
        Optional[str],
        Field(default='0', vo=VoAccess(query=True))
    ]
    create_time: Annotated[
        Optional[datetime],
        BeforeValidator(to_datetime()),
        Field(default=None, vo=VoAccess(query=True))
    ]


class FileShare(AuditEntity):
    """文件分享实体"""

    share_id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(gt=0, default=None, vo=VoAccess(query=True))
    ]
    file_id: Annotated[int, BeforeValidator(str_to_int), Field(gt=0)]
    owner_id: Annotated[int, BeforeValidator(str_to_int), Field(gt=0)]
    target_user_id: Annotated[int, BeforeValidator(str_to_int), Field(gt=0)]
    sym_key_enc: Optional[str] = None
    status: Annotated[
        Optional[str],
        Field(default='0', vo=VoAccess(query=True))
    ]
