# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import List, Dict, Optional
from flask import g

from mapper.chat_mapper import ChatMapper


class ChatService:
    """
    聊天服务层
    """

    @staticmethod
    def get_chat_history(friend_id: int, page: int = 1, page_size: int = 20) -> List[dict]:
        """
        获取历史消息

        Args:
            friend_id: 好友ID
            page: 页码
            page_size: 每页大小

        Returns:
            消息列表
        """
        user_id = g.user.user_id
        return ChatMapper.get_chat_history(user_id, friend_id, page, page_size)

    @staticmethod
    def get_chat_sessions() -> List[dict]:
        """
        获取最近会话列表

        Returns:
            会话列表
        """
        user_id = g.user.user_id
        return ChatMapper.get_chat_sessions(user_id)

    @staticmethod
    def mark_messages_as_read(friend_id: int, user_id: int = None) -> bool:
        """
        标记与某好友的消息为已读

        Args:
            friend_id: 好友ID
            user_id: 用户ID，默认为 None，此时从 g.user 获取

        Returns:
            是否标记成功
        """
        if user_id is None:
            user_id = g.user.user_id
        return ChatMapper.mark_messages_as_read(user_id, friend_id)

    @staticmethod
    def save_message(sender_id: int, receiver_id: int, content: str, msg_type: int = 1) -> int:
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
        return ChatMapper.save_message(sender_id, receiver_id, content, msg_type)

    @staticmethod
    def get_message_create_time(message_id: int) -> str:
        """
        获取消息创建时间

        Args:
            message_id: 消息ID

        Returns:
            创建时间字符串
        """
        return ChatMapper.get_message_create_time(message_id)
