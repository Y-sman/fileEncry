# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import List, Optional
from flask import g

from mapper.friend_mapper import FriendMapper


class FriendService:
    """
    好友服务层
    """

    @staticmethod
    def search_users(keyword: str) -> List[dict]:
        """
        搜索用户

        Args:
            keyword: 搜索关键词

        Returns:
            用户信息列表
        """
        current_user_id = g.user.user_id
        return FriendMapper.search_users(keyword, current_user_id)

    @staticmethod
    def send_friend_request(to_user_id: int, message: str) -> int:
        """
        发送好友申请

        Args:
            to_user_id: 被申请人ID
            message: 申请留言

        Returns:
            申请ID
        """
        from_user_id = g.user.user_id
        return FriendMapper.send_friend_request(from_user_id, to_user_id, message)

    @staticmethod
    def get_pending_requests() -> List[dict]:
        """
        获取待处理的申请列表

        Returns:
            申请列表
        """
        user_id = g.user.user_id
        return FriendMapper.get_pending_requests(user_id)

    @staticmethod
    def handle_friend_request(request_id: int, status: int) -> bool:
        """
        处理好友申请

        Args:
            request_id: 申请ID
            status: 处理状态：1-同意，2-拒绝

        Returns:
            是否处理成功
        """
        return FriendMapper.handle_friend_request(request_id, status)

    @staticmethod
    def get_friend_list() -> List[dict]:
        """
        获取好友列表

        Returns:
            好友列表
        """
        user_id = g.user.user_id
        return FriendMapper.get_friend_list(user_id)

    @staticmethod
    def delete_friend(friend_id: int) -> bool:
        """
        删除好友

        Args:
            friend_id: 好友ID

        Returns:
            是否删除成功
        """
        user_id = g.user.user_id
        return FriendMapper.delete_friend(user_id, friend_id)

    @staticmethod
    def get_friend_public_key(friend_id: int) -> Optional[str]:
        """
        获取好友公钥

        Args:
            friend_id: 好友ID

        Returns:
            公钥字符串，如果不存在则返回None
        """
        return FriendMapper.get_friend_public_key(friend_id)

    @staticmethod
    def get_friend_ids(user_id: int) -> List[int]:
        """
        获取用户的所有好友 ID

        Args:
            user_id: 用户ID

        Returns:
            好友 ID 列表
        """
        return FriendMapper.get_friend_ids(user_id)
