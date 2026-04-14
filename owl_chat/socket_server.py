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
    """
    初始化 SocketIO
    
    Args:
        app: Flask 应用实例
    """
    socketio.init_app(
        app, 
        cors_allowed_origins="*",
        async_mode='threading'
    )
    return socketio


@socketio.on('connect')
def handle_connect():
    """
    处理用户连接
    """
    try:
        # 从请求头获取 token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            # 尝试从查询参数获取 token
            token = request.args.get('token', '')
        
        if not token:
            emit('error', {'message': '缺少认证 token'})
            return False
        
        # 验证 token 并获取用户信息
        login_user = TokenService.get_login_user_from_token(token)
        if not login_user:
            emit('error', {'message': '无效的 token'})
            return False
        
        user_id = login_user.user_id
        
        # 保存用户连接信息
        user_connections[user_id] = request.sid
        
        # 加入用户房间
        room = f"user_{user_id}"
        join_room(room)
        
        # 通知所有好友该用户上线
        friend_ids = FriendService.get_friend_ids(user_id)
        for friend_id in friend_ids:
            friend_room = f"user_{friend_id}"
            emit('user.online', {'user_id': user_id}, room=friend_room)
        
        # 发送连接成功消息
        emit('connected', {'user_id': user_id, 'message': '连接成功'})
        
    except Exception as e:
        print(f"连接处理错误: {e}")
        emit('error', {'message': '连接失败'})
        return False


@socketio.on('disconnect')
def handle_disconnect():
    """
    处理用户断开连接
    """
    try:
        # 查找断开连接的用户
        disconnected_user_id = None
        for user_id, sid in user_connections.items():
            if sid == request.sid:
                disconnected_user_id = user_id
                break
        
        if disconnected_user_id:
            # 从连接信息中移除
            del user_connections[disconnected_user_id]
            
            # 离开用户房间
            room = f"user_{disconnected_user_id}"
            leave_room(room)
            
            # 通知所有好友该用户下线
            friend_ids = FriendService.get_friend_ids(disconnected_user_id)
            for friend_id in friend_ids:
                friend_room = f"user_{friend_id}"
                emit('user.offline', {'user_id': disconnected_user_id}, room=friend_room)
    except Exception as e:
        print(f"断开连接处理错误: {e}")


@socketio.on('chat.message')
def handle_chat_message(data):
    """
    处理聊天消息
    
    Args:
        data: 消息数据，包含 receiver_id, content, msg_type
    """
    try:
        # 从连接信息中获取发送者 ID
        sender_id = None
        for user_id, sid in user_connections.items():
            if sid == request.sid:
                sender_id = user_id
                break
        
        if not sender_id:
            emit('error', {'message': '未找到发送者信息'})
            return
        
        # 提取消息数据
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        msg_type = data.get('msg_type', 1)  # 默认消息类型为 1（文本）
        
        if not receiver_id or not content:
            emit('error', {'message': '缺少必要的消息参数'})
            return
        
        # 保存消息到数据库
        message_id = ChatService.save_message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            msg_type=msg_type
        )
        
        # 准备消息数据
        message_data = {
            'message_id': message_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'content': content,
            'msg_type': msg_type,
            'create_time': ChatService.get_message_create_time(message_id)
        }
        
        # 推送给接收者
        receiver_room = f"user_{receiver_id}"
        emit('chat.message', message_data, room=receiver_room)
        
        # 同时发送给发送者（确认消息已发送）
        emit('chat.message.sent', message_data)
        
    except Exception as e:
        print(f"消息处理错误: {e}")
        emit('error', {'message': '消息发送失败'})


@socketio.on('chat.read')
def handle_chat_read(data):
    """
    处理消息已读
    
    Args:
        data: 数据，包含 friend_id
    """
    try:
        # 从连接信息中获取用户 ID
        user_id = None
        for uid, sid in user_connections.items():
            if sid == request.sid:
                user_id = uid
                break
        
        if not user_id:
            emit('error', {'message': '未找到用户信息'})
            return
        
        # 提取好友 ID
        friend_id = data.get('friend_id')
        if not friend_id:
            emit('error', {'message': '缺少好友 ID'})
            return
        
        # 标记消息为已读
        ChatService.mark_messages_as_read(user_id, friend_id)
        
        # 发送确认消息
        emit('chat.read.ack', {'friend_id': friend_id, 'message': '消息已标记为已读'})
        
    except Exception as e:
        print(f"消息已读处理错误: {e}")
        emit('error', {'message': '标记消息已读失败'})
