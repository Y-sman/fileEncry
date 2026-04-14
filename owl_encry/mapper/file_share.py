# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import List, Optional
from sqlalchemy.orm import Session

from owl_encry.domain.po import FileSharePo
from owl_admin.ext import db


class FileShareMapper:
    """文件分享映射器"""

    @staticmethod
    def insert(share: FileSharePo) -> int:
        """插入分享记录"""
        try:
            db.session.add(share)
            db.session.commit()
            return share.share_id
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def select_by_id(share_id: int) -> Optional[FileSharePo]:
        """根据ID查询分享记录"""
        return db.session.query(FileSharePo).filter(
            FileSharePo.share_id == share_id,
            FileSharePo.status == 0
        ).first()

    @staticmethod
    def select_by_file_and_target(file_id: int, target_user_id: int) -> Optional[FileSharePo]:
        """根据文件ID和目标用户ID查询分享记录"""
        return db.session.query(FileSharePo).filter(
            FileSharePo.file_id == file_id,
            FileSharePo.target_user_id == target_user_id,
            FileSharePo.status == 0
        ).first()

    @staticmethod
    def select_by_owner(owner_id: int) -> List[FileSharePo]:
        """查询用户分享的文件"""
        return db.session.query(FileSharePo).filter(
            FileSharePo.owner_id == owner_id,
            FileSharePo.status == 0
        ).all()

    @staticmethod
    def select_by_target(target_user_id: int) -> List[FileSharePo]:
        """查询分享给用户的文件"""
        return db.session.query(FileSharePo).filter(
            FileSharePo.target_user_id == target_user_id,
            FileSharePo.status == 0
        ).all()

    @staticmethod
    def update_status(share_id: int, status: str) -> int:
        """更新分享状态"""
        try:
            result = db.session.query(FileSharePo).filter(
                FileSharePo.share_id == share_id
            ).update({'status': status})
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise e