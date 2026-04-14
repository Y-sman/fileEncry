# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import List, Optional
from sqlalchemy import and_, or_, insert, select, update, delete
from sqlalchemy.orm import Session

from owl_admin.ext import db
from owl_system.domain.po import SysUserPo
from owl_encry.domain.po import EncUserKeyPo


class FriendMapper:
    """
    好友关系数据访问层
    """

    @classmethod
    def search_users(cls, keyword: str, current_user_id: int) -> List[dict]:
        """
        搜索用户（按用户名/昵称模糊匹配）

        Args:
            keyword: 搜索关键词
            current_user_id: 当前用户ID

        Returns:
            用户信息列表
        """
        # 搜索用户，排除当前用户
        stmt = select(
            SysUserPo.user_id,
            SysUserPo.user_name,
            SysUserPo.nick_name,
            SysUserPo.avatar,
            SysUserPo.status
        ).where(
            and_(
                SysUserPo.del_flag == "0",
                SysUserPo.user_id != current_user_id,
                or_(
                    SysUserPo.user_name.like(f"%{keyword}%"),
                    SysUserPo.nick_name.like(f"%{keyword}%")
                )
            )
        )
        rows = db.session.execute(stmt).all()

        # 转换为字典列表
        users = []
        for row in rows:
            users.append({
                "user_id": row.user_id,
                "user_name": row.user_name,
                "nick_name": row.nick_name,
                "avatar": row.avatar,
                "status": row.status
            })
        return users

    @classmethod
    def send_friend_request(cls, from_user_id: int, to_user_id: int, message: str) -> int:
        """
        发送好友申请

        Args:
            from_user_id: 申请人ID
            to_user_id: 被申请人ID
            message: 申请留言

        Returns:
            申请ID
        """
        # 插入好友申请
        stmt = insert(db.Model.metadata.tables['sys_friend_request']).values(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            message=message,
            status=0  # 0-待处理
        )
        result = db.session.execute(stmt)
        # 获取插入的ID
        request_id = result.inserted_primary_key[0]
        # 提交事务
        db.session.commit()
        return request_id

    @classmethod
    def get_pending_requests(cls, user_id: int) -> List[dict]:
        """
        获取待处理的申请列表

        Args:
            user_id: 用户ID

        Returns:
            申请列表
        """
        # 查询待处理的申请
        request_table = db.Model.metadata.tables['sys_friend_request']
        stmt = select(
            request_table.c.id,
            request_table.c.from_user_id,
            request_table.c.message,
            request_table.c.create_time,
            SysUserPo.user_name,
            SysUserPo.nick_name,
            SysUserPo.avatar
        ).join(
            SysUserPo, request_table.c.from_user_id == SysUserPo.user_id
        ).where(
            and_(
                request_table.c.to_user_id == user_id,
                request_table.c.status == 0  # 0-待处理
            )
        )
        rows = db.session.execute(stmt).all()

        # 转换为字典列表
        requests = []
        for row in rows:
            requests.append({
                "id": row.id,
                "from_user_id": row.from_user_id,
                "message": row.message,
                "create_time": row.create_time,
                "user_name": row.user_name,
                "nick_name": row.nick_name,
                "avatar": row.avatar
            })
        return requests

    @classmethod
    def handle_friend_request(cls, request_id: int, status: int) -> bool:
        """
        处理好友申请

        Args:
            request_id: 申请ID
            status: 处理状态：1-同意，2-拒绝

        Returns:
            是否处理成功
        """
        # 更新申请状态
        request_table = db.Model.metadata.tables['sys_friend_request']
        stmt = update(request_table).where(
            request_table.c.id == request_id
        ).values(
            status=status,
            handle_time=db.func.current_timestamp()
        )
        result = db.session.execute(stmt)
        db.session.commit()

        # 如果同意申请，创建好友关系
        if status == 1:
            # 查询申请信息
            request_stmt = select(
                request_table.c.from_user_id,
                request_table.c.to_user_id
            ).where(
                request_table.c.id == request_id
            )
            request = db.session.execute(request_stmt).one()
            from_user_id = request.from_user_id
            to_user_id = request.to_user_id

            # 创建双向好友关系
            friend_table = db.Model.metadata.tables['sys_user_friend']
            # 插入from_user -> to_user的关系
            insert_stmt1 = insert(friend_table).values(
                user_id=from_user_id,
                friend_id=to_user_id,
                status=1  # 1-已添加
            )
            # 插入to_user -> from_user的关系
            insert_stmt2 = insert(friend_table).values(
                user_id=to_user_id,
                friend_id=from_user_id,
                status=1  # 1-已添加
            )
            db.session.execute(insert_stmt1)
            db.session.execute(insert_stmt2)
            db.session.commit()

        return result.rowcount > 0

    @classmethod
    def get_friend_list(cls, user_id: int) -> List[dict]:
        """
        获取好友列表

        Args:
            user_id: 用户ID

        Returns:
            好友列表
        """
        # 查询好友关系
        friend_table = db.Model.metadata.tables['sys_user_friend']
        stmt = select(
            SysUserPo.user_id,
            SysUserPo.user_name,
            SysUserPo.nick_name,
            SysUserPo.avatar,
            SysUserPo.status
        ).join(
            friend_table, SysUserPo.user_id == friend_table.c.friend_id
        ).where(
            and_(
                friend_table.c.user_id == user_id,
                friend_table.c.status == 1  # 1-已添加
            )
        )
        rows = db.session.execute(stmt).all()

        # 转换为字典列表
        friends = []
        for row in rows:
            friends.append({
                "user_id": row.user_id,
                "user_name": row.user_name,
                "nick_name": row.nick_name,
                "avatar": row.avatar,
                "status": row.status
            })
        return friends

    @classmethod
    def delete_friend(cls, user_id: int, friend_id: int) -> bool:
        """
        删除好友

        Args:
            user_id: 用户ID
            friend_id: 好友ID

        Returns:
            是否删除成功
        """
        # 删除双向好友关系
        friend_table = db.Model.metadata.tables['sys_user_friend']
        # 删除user_id -> friend_id的关系
        delete_stmt1 = delete(friend_table).where(
            and_(
                friend_table.c.user_id == user_id,
                friend_table.c.friend_id == friend_id
            )
        )
        # 删除friend_id -> user_id的关系
        delete_stmt2 = delete(friend_table).where(
            and_(
                friend_table.c.user_id == friend_id,
                friend_table.c.friend_id == user_id
            )
        )
        result1 = db.session.execute(delete_stmt1)
        result2 = db.session.execute(delete_stmt2)
        db.session.commit()

        return (result1.rowcount > 0) or (result2.rowcount > 0)

    @classmethod
    def get_friend_public_key(cls, friend_id: int) -> Optional[str]:
        """
        获取好友公钥

        Args:
            friend_id: 好友ID

        Returns:
            公钥字符串，如果不存在则返回None
        """
        # 查询用户公钥
        stmt = select(EncUserKeyPo.public_key).where(
            and_(
                EncUserKeyPo.user_id == friend_id,
                EncUserKeyPo.status == "0"  # 0-正常
            )
        )
        result = db.session.execute(stmt).one_or_none()
        return result.public_key if result else None

    @classmethod
    def get_friend_ids(cls, user_id: int) -> List[int]:
        """
        获取用户的所有好友 ID

        Args:
            user_id: 用户ID

        Returns:
            好友 ID 列表
        """
        # 查询好友关系
        friend_table = db.Model.metadata.tables['sys_user_friend']
        stmt = select(
            friend_table.c.friend_id
        ).where(
            and_(
                friend_table.c.user_id == user_id,
                friend_table.c.status == 1  # 1-已添加
            )
        )
        rows = db.session.execute(stmt).all()
        
        # 转换为 ID 列表
        friend_ids = [row.friend_id for row in rows]
        return friend_ids
