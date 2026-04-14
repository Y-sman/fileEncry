# -*- coding: utf-8 -*-
"""
WebSocket 聊天服务
"""

from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room

from owl_framework.service.token import TokenService
from service.friend_service import FriendService
from service.chat_service import ChatService

# 创建 SocketIO 实例
socketio = SocketIO()

# 存储用户连接信息
user_connections = {}


def init_socketio(app):
    """初始化 SocketIO。"""
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode='threading'
    )
    return socketio


@socketio.on('connect')
def handle_connect():
    """处理用户连接。"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            token = request.args.get('token', '')

        if not token:
            emit('error', {'message': '缺少认证 token'})
            return False

        login_user = TokenService.get_login_user_from_token(token)
        if not login_user:
            emit('error', {'message': '无效的 token'})
            return False

        user_id = login_user.user_id
        user_connections[user_id] = request.sid

        room = f"user_{user_id}"
        join_room(room)

        friend_ids = FriendService.get_friend_ids(user_id)
        for friend_id in friend_ids:
            emit('user.online', {'user_id': user_id}, room=f"user_{friend_id}")

        emit('connected', {'user_id': user_id, 'message': '连接成功'})
    except Exception as e:
        print(f"连接处理错误: {e}")
        emit('error', {'message': '连接失败'})
        return False


@socketio.on('disconnect')
def handle_disconnect():
    """处理用户断开连接。"""
    try:
        disconnected_user_id = None
        for user_id, sid in user_connections.items():
            if sid == request.sid:
                disconnected_user_id = user_id
                break

        if disconnected_user_id:
            del user_connections[disconnected_user_id]
            leave_room(f"user_{disconnected_user_id}")

            friend_ids = FriendService.get_friend_ids(disconnected_user_id)
            for friend_id in friend_ids:
                emit('user.offline', {'user_id': disconnected_user_id}, room=f"user_{friend_id}")
    except Exception as e:
        print(f"断开连接处理错误: {e}")


@socketio.on('chat.message')
def handle_chat_message(data):
    """处理聊天消息。"""
    try:
        sender_id = None
        for user_id, sid in user_connections.items():
            if sid == request.sid:
                sender_id = user_id
                break

        if not sender_id:
            emit('error', {'message': '未找到发送者信息'})
            return

        receiver_id = data.get('receiver_id')
        content = data.get('content')
        msg_type = data.get('msg_type', 1)
        file_id = data.get('file_id')

        if not receiver_id or not content:
            emit('error', {'message': '缺少必要的消息参数'})
            return

        message_id = ChatService.save_message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            msg_type=msg_type,
            file_id=file_id
        )

        message_data = {
            'message_id': message_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'content': content,
            'msg_type': msg_type,
            'file_id': file_id,
            'create_time': ChatService.get_message_create_time(message_id)
        }

        emit('chat.message', message_data, room=f"user_{receiver_id}")
        emit('chat.message.sent', message_data)
    except Exception as e:
        print(f"消息处理错误: {e}")
        emit('error', {'message': '消息发送失败'})


@socketio.on('chat.read')
def handle_chat_read(data):
    """处理消息已读。"""
    try:
        user_id = None
        for uid, sid in user_connections.items():
            if sid == request.sid:
                user_id = uid
                break

        if not user_id:
            emit('error', {'message': '未找到用户信息'})
            return

        friend_id = data.get('friend_id')
        if not friend_id:
            emit('error', {'message': '缺少好友 ID'})
            return

        ChatService.mark_messages_as_read(user_id, friend_id)
        emit('chat.read.ack', {'friend_id': friend_id, 'message': '消息已标记为已读'})
    except Exception as e:
        print(f"消息已读处理错误: {e}")
        emit('error', {'message': '标记消息已读失败'})
