# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import List, Dict, Optional
from sqlalchemy import and_, or_, select, update, func

from owl_admin.ext import db
from owl_system.domain.po import SysUserPo


class ChatMapper:
    """
    聊天数据访问层
    """

    @classmethod
    def get_chat_history(cls, user_id: int, friend_id: int, page: int, page_size: int) -> List[dict]:
        """
        获取历史消息

        Args:
            user_id: 用户ID
            friend_id: 好友ID
            page: 页码
            page_size: 每页大小

        Returns:
            消息列表
        """
        message_table = db.Model.metadata.tables['chat_message']
        # 计算偏移量
        offset = (page - 1) * page_size
        # 查询用户与好友之间的消息，按时间倒序排列
        stmt = select(
            message_table.c.id,
            message_table.c.sender_id,
            message_table.c.receiver_id,
            message_table.c.msg_type,
            message_table.c.content,
            message_table.c.file_id,
            message_table.c.is_read,
            message_table.c.create_time
        ).where(
            or_(
                and_(
                    message_table.c.sender_id == user_id,
                    message_table.c.receiver_id == friend_id
                ),
                and_(
                    message_table.c.sender_id == friend_id,
                    message_table.c.receiver_id == user_id
                )
            )
        ).order_by(message_table.c.create_time.desc()).limit(page_size).offset(offset)
        rows = db.session.execute(stmt).all()

        # 转换为字典列表，并反转顺序（使时间正序）
        messages = []
        for row in rows:
            messages.append({
                "id": row.id,
                "sender_id": row.sender_id,
                "receiver_id": row.receiver_id,
                "msg_type": row.msg_type,
                "content": row.content,
                "file_id": row.file_id,
                "is_read": row.is_read,
                "create_time": row.create_time
            })
        # 反转列表，使消息按时间正序排列
        messages.reverse()
        return messages

    @classmethod
    def get_chat_sessions(cls, user_id: int) -> List[dict]:
        """
        获取最近会话列表

        Args:
            user_id: 用户ID

        Returns:
            会话列表
        """
        session_table = db.Model.metadata.tables['chat_session']
        message_table = db.Model.metadata.tables['chat_message']
        # 查询用户的所有会话，按最后消息时间倒序排列
        stmt = select(
            session_table.c.id,
            session_table.c.friend_id,
            session_table.c.last_msg_id,
            session_table.c.last_msg_time,
            session_table.c.unread_count,
            SysUserPo.user_name,
            SysUserPo.nick_name,
            SysUserPo.avatar,
            message_table.c.content.label('last_msg_content'),
            message_table.c.msg_type.label('last_msg_type')
        ).join(
            SysUserPo, session_table.c.friend_id == SysUserPo.user_id
        ).outerjoin(
            message_table, session_table.c.last_msg_id == message_table.c.id
        ).where(
            session_table.c.user_id == user_id
        ).order_by(session_table.c.last_msg_time.desc())
        rows = db.session.execute(stmt).all()

        # 转换为字典列表
        sessions = []
        for row in rows:
            sessions.append({
                "id": row.id,
                "friend_id": row.friend_id,
                "user_name": row.user_name,
                "nick_name": row.nick_name,
                "avatar": row.avatar,
                "last_msg_id": row.last_msg_id,
                "last_msg_content": row.last_msg_content,
                "last_msg_type": row.last_msg_type,
                "last_msg_time": row.last_msg_time,
                "unread_count": row.unread_count
            })
        return sessions

    @classmethod
    def mark_messages_as_read(cls, user_id: int, friend_id: int) -> bool:
        """
        标记与某好友的消息为已读

        Args:
            user_id: 用户ID
            friend_id: 好友ID

        Returns:
            是否标记成功
        """
        try:
            message_table = db.Model.metadata.tables['chat_message']
            # 更新消息为已读
            update_stmt = update(message_table).where(
                and_(
                    message_table.c.sender_id == friend_id,
                    message_table.c.receiver_id == user_id,
                    message_table.c.is_read == 0
                )
            ).values(is_read=1)
            db.session.execute(update_stmt)

            # 更新会话表中的未读消息数
            session_table = db.Model.metadata.tables['chat_session']
            # 计算未读消息数
            unread_count_stmt = select(func.count()).select_from(message_table).where(
                and_(
                    message_table.c.sender_id == friend_id,
                    message_table.c.receiver_id == user_id,
                    message_table.c.is_read == 0
                )
            )
            unread_count = db.session.execute(unread_count_stmt).scalar() or 0

            # 更新会话表
            update_session_stmt = update(session_table).where(
                and_(
                    session_table.c.user_id == user_id,
                    session_table.c.friend_id == friend_id
                )
            ).values(unread_count=unread_count)
            db.session.execute(update_session_stmt)

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"标记已读失败: {e}")
            return False

    @classmethod
    def save_message(
        cls,
        sender_id: int,
        receiver_id: int,
        content: str,
        msg_type: int = 1,
        file_id: int = None
    ) -> int:
        """
        保存聊天消息

        Args:
            sender_id: 发送者ID
            receiver_id: 接收者ID
            content: 消息内容
            msg_type: 消息类型，默认 1（文本）

        Returns:
            消息ID
        """
        message_table = db.Model.metadata.tables['chat_message']
        session_table = db.Model.metadata.tables['chat_session']

        # 插入消息
        from sqlalchemy import insert
        stmt = insert(message_table).values(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            msg_type=msg_type,
            file_id=file_id,
            is_read=0  # 默认未读
        )
        result = db.session.execute(stmt)
        message_id = result.inserted_primary_key[0]

        # 获取消息创建时间
        time_stmt = select(message_table.c.create_time).where(message_table.c.id == message_id)
        create_time = db.session.execute(time_stmt).scalar()

        # 检查发送者的会话是否存在
        sender_session_stmt = select(session_table.c.id).where(
            and_(
                session_table.c.user_id == sender_id,
                session_table.c.friend_id == receiver_id
            )
        )
        sender_session = db.session.execute(sender_session_stmt).scalar()

        # 如果发送者的会话不存在，创建会话
        if not sender_session:
            insert_session_stmt = insert(session_table).values(
                user_id=sender_id,
                friend_id=receiver_id,
                last_msg_id=message_id,
                last_msg_time=create_time,
                unread_count=0
            )
            db.session.execute(insert_session_stmt)
        else:
            # 更新发送者的会话
            update_session_stmt = update(session_table).where(
                and_(
                    session_table.c.user_id == sender_id,
                    session_table.c.friend_id == receiver_id
                )
            ).values(
                last_msg_id=message_id,
                last_msg_time=create_time
            )
            db.session.execute(update_session_stmt)

        # 检查接收者的会话是否存在
        receiver_session_stmt = select(session_table.c.id).where(
            and_(
                session_table.c.user_id == receiver_id,
                session_table.c.friend_id == sender_id
            )
        )
        receiver_session = db.session.execute(receiver_session_stmt).scalar()

        # 如果接收者的会话不存在，创建会话
        if not receiver_session:
            insert_session_stmt = insert(session_table).values(
                user_id=receiver_id,
                friend_id=sender_id,
                last_msg_id=message_id,
                last_msg_time=create_time,
                unread_count=1  # 新消息未读
            )
            db.session.execute(insert_session_stmt)
        else:
            # 更新接收者的会话，增加未读消息数
            update_session_stmt = update(session_table).where(
                and_(
                    session_table.c.user_id == receiver_id,
                    session_table.c.friend_id == sender_id
                )
            ).values(
                last_msg_id=message_id,
                last_msg_time=create_time,
                unread_count=session_table.c.unread_count + 1
            )
            db.session.execute(update_session_stmt)

        db.session.commit()
        return message_id

    @classmethod
    def get_message_create_time(cls, message_id: int) -> str:
        """
        获取消息创建时间

        Args:
            message_id: 消息ID

        Returns:
            创建时间字符串
        """
        message_table = db.Model.metadata.tables['chat_message']
        stmt = select(message_table.c.create_time).where(message_table.c.id == message_id)
        result = db.session.execute(stmt).scalar()
        return str(result) if result else ""
