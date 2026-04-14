# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from owl_common.sqlalchemy.model import ColumnEntityList
from owl_common.sqlalchemy.transaction import Transactional
from owl_encry.domain.entity import EncUserKey
from owl_encry.domain.po import EncUserKeyPo
from owl_admin.ext import db


class EncUserKeyMapper:

    default_fields = {
        "key_id", "user_id", "public_key", "private_key_enc",
        "key_size", "status", "create_by", "create_time",
        "update_by", "update_time", "remark"
    }

    default_columns = ColumnEntityList(EncUserKeyPo, default_fields, False)

    @classmethod
    def select_by_user_id(cls, user_id: int) -> Optional[EncUserKey]:
        """根据用户ID查询密钥"""
        columns = ColumnEntityList(EncUserKeyPo, cls.default_fields, False)
        stmt = select(*columns).where(EncUserKeyPo.user_id == user_id)
        row = db.session.execute(stmt).one_or_none()
        return columns.cast(row, EncUserKey) if row else None

    @classmethod
    def select_by_id(cls, key_id: int) -> Optional[EncUserKey]:
        """根据密钥ID查询"""
        columns = ColumnEntityList(EncUserKeyPo, cls.default_fields, False)
        stmt = select(*columns).where(EncUserKeyPo.key_id == key_id)
        row = db.session.execute(stmt).one_or_none()
        return columns.cast(row, EncUserKey) if row else None

    @classmethod
    @Transactional(db.session)
    def insert(cls, key: EncUserKey) -> int:
        """新增密钥"""
        from sqlalchemy import insert
        fields = {"user_id", "public_key", "private_key_enc", "key_size",
                  "status", "create_by", "create_time", "remark"}
        data = key.model_dump(include=fields, exclude_unset=True, exclude_none=True)
        stmt = insert(EncUserKeyPo).values(**data)
        out = db.session.execute(stmt).inserted_primary_key
        return out[0] if out else 0

    @classmethod
    @Transactional(db.session)
    def update(cls, key: EncUserKey) -> int:
        """更新密钥"""
        from sqlalchemy import update as sa_update
        fields = {"public_key", "private_key_enc", "key_size", "status",
                  "update_by", "update_time", "remark"}
        data = key.model_dump(include=fields, exclude_unset=True, exclude_none=True)
        stmt = sa_update(EncUserKeyPo).where(EncUserKeyPo.key_id == key.key_id).values(**data)
        return db.session.execute(stmt).rowcount

    @classmethod
    @Transactional(db.session)
    def delete_by_user_id(cls, user_id: int) -> int:
        """删除用户密钥"""
        from sqlalchemy import delete
        stmt = delete(EncUserKeyPo).where(EncUserKeyPo.user_id == user_id)
        return db.session.execute(stmt).rowcount
