# -*- coding: utf-8 -*-
# @Author  : balabala

from flask import request

from owl_framework.descriptor.permission import PreAuthorize, HasPerm
from owl_common.descriptor.serializer import JsonSerializer
from owl_common.base.model import AjaxResponse
from service.chat_service import ChatService

# 导入 reg，如果失败则尝试从 sys.modules 获取
try:
    from ... import reg
except ImportError:
    import sys
    owl_admin = sys.modules.get('owl_admin')
    if owl_admin and hasattr(owl_admin, 'reg'):
        reg = owl_admin.reg
    else:
        raise


@reg.api.route('/chat/history/<int:friendId>', methods=['GET'])
@PreAuthorize(HasPerm("chat:history"))
@JsonSerializer()
def get_chat_history(friendId):
    """
    获取历史消息
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    messages = ChatService.get_chat_history(friendId, page, page_size)
    return AjaxResponse.from_success(data=messages)


@reg.api.route('/chat/sessions', methods=['GET'])
@PreAuthorize(HasPerm("chat:sessions"))
@JsonSerializer()
def get_chat_sessions():
    """
    获取最近会话列表
    """
    sessions = ChatService.get_chat_sessions()
    return AjaxResponse.from_success(data=sessions)


@reg.api.route('/chat/read/<int:friendId>', methods=['PUT'])
@PreAuthorize(HasPerm("chat:read"))
@JsonSerializer()
def mark_messages_as_read(friendId):
    """
    标记与某好友的消息为已读
    """
    success = ChatService.mark_messages_as_read(friendId)
    if success:
        return AjaxResponse.from_success(msg="标记成功")
    else:
        return AjaxResponse.from_error(msg="标记失败")
