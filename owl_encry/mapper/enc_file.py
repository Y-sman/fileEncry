# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import List, Optional
from sqlalchemy import select, or_, func
from flask import g

from owl_common.base.model import ExtraModel
from owl_common.sqlalchemy.model import ColumnEntityList
from owl_common.sqlalchemy.query import Pagination
from owl_common.sqlalchemy.transaction import Transactional
from owl_encry.domain.entity import EncFile
from owl_encry.domain.po import EncFilePo
from owl_admin.ext import db


class EncFileMapper:

    default_fields = {
        "file_id", "user_id", "original_name", "stored_name", "file_path",
        "file_size", "encrypt_algo", "sym_key_enc", "iv", "file_hash", "del_flag",
        "create_by", "create_time", "update_by", "update_time", "remark"
    }

    default_columns = ColumnEntityList(EncFilePo, default_fields, False)

    @classmethod
    def select_list(cls, query: EncFile) -> List[EncFile]:
        """根据条件查询文件列表（必须按 user_id 过滤，保障用户数据隔离）"""
        columns = ColumnEntityList(EncFilePo, cls.default_fields, False)
        criterions = [EncFilePo.del_flag == '0']
        if query.user_id is None or query.user_id <= 0:
            return []
        criterions.append(EncFilePo.user_id == query.user_id)
        if query.original_name:
            criterions.append(EncFilePo.original_name.like(f"%{query.original_name}%"))
        if query.encrypt_algo:
            algo = (query.encrypt_algo or '').strip().upper()
            if algo == 'AES':
                criterions.append(EncFilePo.encrypt_algo.like('AES%'))
            else:
                criterions.append(EncFilePo.encrypt_algo == algo)
        if g.criterian_meta.extra:
            extra: ExtraModel = g.criterian_meta.extra
            if extra.start_time and extra.end_time:
                criterions.append(EncFilePo.create_time >= extra.start_time)
                criterions.append(EncFilePo.create_time <= extra.end_time)
        if g.criterian_meta.scope:
            criterions.append(g.criterian_meta.scope)

        stmt = select(*columns).where(*criterions).order_by(EncFilePo.create_time.desc())
        page = g.criterian_meta.page
        if page:
            pagination = Pagination(page_num=page.page_num, page_size=page.page_size)
            page.total = pagination.compute_count(stmt, db.session)
            stmt = pagination.rebuild(stmt)
        rows = db.session.execute(stmt).all()
        return [columns.cast(row, EncFile) for row in rows]

    @classmethod
    def select_by_id(cls, file_id: int) -> Optional[EncFile]:
        """根据文件ID查询"""
        columns = ColumnEntityList(EncFilePo, cls.default_fields, False)
        stmt = select(*columns).where(
            EncFilePo.file_id == file_id,
            EncFilePo.del_flag == '0'
        )
        row = db.session.execute(stmt).one_or_none()
        return columns.cast(row, EncFile) if row else None

    @classmethod
    def count_by_user_id(cls, user_id: int) -> int:
        """当前用户文件数量（未删除）"""
        stmt = select(func.count()).select_from(EncFilePo).where(
            EncFilePo.user_id == user_id,
            EncFilePo.del_flag == '0'
        )
        return db.session.execute(stmt).scalar() or 0

    @classmethod
    def sum_storage_by_user_id(cls, user_id: int) -> int:
        """当前用户存储占用（字节）"""
        stmt = select(func.coalesce(func.sum(EncFilePo.file_size), 0)).where(
            EncFilePo.user_id == user_id,
            EncFilePo.del_flag == '0'
        )
        return int(db.session.execute(stmt).scalar() or 0)

    @classmethod
    def select_by_id_and_user(cls, file_id: int, user_id: int) -> Optional[EncFile]:
        """根据文件ID和用户ID查询"""
        columns = ColumnEntityList(EncFilePo, cls.default_fields, False)
        stmt = select(*columns).where(
            EncFilePo.file_id == file_id,
            EncFilePo.user_id == user_id,
            EncFilePo.del_flag == '0'
        )
        row = db.session.execute(stmt).one_or_none()
        return columns.cast(row, EncFile) if row else None

    @classmethod
    @Transactional(db.session)
    def insert(cls, file: EncFile) -> int:
        """新增文件记录"""
        from sqlalchemy import insert
        fields = {"user_id", "original_name", "stored_name", "file_path",
                  "file_size", "encrypt_algo", "sym_key_enc", "iv", "file_hash",
                  "del_flag", "create_by", "create_time", "remark"}
        data = file.model_dump(include=fields, exclude_unset=True, exclude_none=True)
        stmt = insert(EncFilePo).values(**data)
        out = db.session.execute(stmt).inserted_primary_key
        return out[0] if out else 0

    @classmethod
    @Transactional(db.session)
    def delete_by_id(cls, file_id: int) -> int:
        """逻辑删除文件"""
        from sqlalchemy import update
        stmt = update(EncFilePo).where(EncFilePo.file_id == file_id).values(del_flag='2')
        return db.session.execute(stmt).rowcount

    @classmethod
    @Transactional(db.session)
    def delete_by_ids(cls, file_ids: List[int]) -> int:
        """批量逻辑删除"""
        from sqlalchemy import update
        stmt = update(EncFilePo).where(EncFilePo.file_id.in_(file_ids)).values(del_flag='2')
        return db.session.execute(stmt).rowcount

    @classmethod
    def total_storage(cls) -> int:
        """全系统加密文件存储总量（字节），供管理员监控"""
        stmt = select(func.coalesce(func.sum(EncFilePo.file_size), 0)).where(EncFilePo.del_flag == '0')
        return int(db.session.execute(stmt).scalar() or 0)
