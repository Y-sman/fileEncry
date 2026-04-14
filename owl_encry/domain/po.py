# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import Optional
from sqlalchemy import CHAR, DateTime, String, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column
import datetime

from owl_admin.ext import db


class EncUserKeyPo(db.Model):
    """用户RSA密钥对表"""
    __tablename__ = 'enc_user_key'
    __table_args__ = {'comment': '用户RSA密钥对表'}

    key_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True, autoincrement=True, comment='密钥ID')
    user_id: Mapped[int] = mapped_column(BIGINT(20), nullable=False, comment='用户ID')
    public_key: Mapped[str] = mapped_column(TEXT, nullable=False, comment='RSA公钥(PEM格式)')
    private_key_enc: Mapped[str] = mapped_column(TEXT, nullable=False, comment='RSA私钥(加密存储)')
    key_size: Mapped[int] = mapped_column(INTEGER(4), server_default=text("'2048'"), comment='密钥长度(2048/4096)')
    status: Mapped[str] = mapped_column(CHAR(1), server_default=text("'0'"), comment='状态(0正常 1停用)')
    create_by: Mapped[Optional[str]] = mapped_column(String(64), server_default=text("''"), comment='创建者')
    create_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='创建时间')
    update_by: Mapped[Optional[str]] = mapped_column(String(64), server_default=text("''"), comment='更新者')
    update_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='更新时间')
    remark: Mapped[Optional[str]] = mapped_column(String(500), comment='备注')


class EncFilePo(db.Model):
    """加密文件表"""
    __tablename__ = 'enc_file'
    __table_args__ = {'comment': '加密文件表'}

    file_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True, autoincrement=True, comment='文件ID')
    user_id: Mapped[int] = mapped_column(BIGINT(20), nullable=False, comment='所属用户ID')
    original_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='原始文件名')
    stored_name: Mapped[str] = mapped_column(String(64), nullable=False, comment='存储文件名(UUID)')
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment='文件存储路径')
    file_size: Mapped[int] = mapped_column(BIGINT(20), server_default=text("'0'"), comment='文件大小(字节)')
    encrypt_algo: Mapped[str] = mapped_column(String(20), nullable=False, comment='对称加密算法(AES/DES)')
    sym_key_enc: Mapped[str] = mapped_column(TEXT, nullable=False, comment='对称密钥(RSA加密后存储)')
    iv: Mapped[Optional[str]] = mapped_column(String(64), server_default=text("''"), comment='加密向量/IV(Base64)')
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), comment='原始文件SHA256哈希(十六进制)')
    del_flag: Mapped[str] = mapped_column(CHAR(1), server_default=text("'0'"), comment='删除标志(0存在 2删除)')
    create_by: Mapped[Optional[str]] = mapped_column(String(64), server_default=text("''"), comment='创建者')
    create_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='创建时间')
    update_by: Mapped[Optional[str]] = mapped_column(String(64), server_default=text("''"), comment='更新者')
    update_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='更新时间')
    remark: Mapped[Optional[str]] = mapped_column(String(500), comment='备注')


class FileSharePo(db.Model):
    """文件分享表"""
    __tablename__ = 'enc_file_share'
    __table_args__ = {'comment': '文件分享表'}

    share_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True, autoincrement=True, comment='分享ID')
    file_id: Mapped[int] = mapped_column(BIGINT(20), nullable=False, comment='文件ID')
    owner_id: Mapped[int] = mapped_column(BIGINT(20), nullable=False, comment='分享者ID')
    target_user_id: Mapped[int] = mapped_column(BIGINT(20), nullable=False, comment='目标用户ID')
    sym_key_enc: Mapped[str] = mapped_column(TEXT, nullable=False, comment='用接收者公钥加密的AES密钥')
    permissions: Mapped[Optional[str]] = mapped_column(String(10), server_default=text("'READ'"), comment='权限: READ-只读')
    share_from_chat: Mapped[Optional[int]] = mapped_column(INTEGER(4), server_default=text("'0'"), comment='是否从聊天分享: 0-否 1-是')
    expire_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='过期时间')
    status: Mapped[Optional[int]] = mapped_column(INTEGER(4), server_default=text("'0'"), comment='状态: 0-有效 1-已撤销 2-已过期')
    create_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
