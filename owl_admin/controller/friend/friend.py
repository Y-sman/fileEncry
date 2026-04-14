# -*- coding: utf-8 -*-
# @Author  : balabala

from flask import request

from owl_framework.descriptor.permission import PreAuthorize, HasPerm
from owl_common.descriptor.serializer import JsonSerializer
from owl_common.base.model import AjaxResponse
from service.friend_service import FriendService

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


@reg.api.route('/friend/search', methods=['GET'])
@PreAuthorize(HasPerm("friend:search"))
@JsonSerializer()
def search_users():
    """
    搜索用户
    """
    keyword = request.args.get('keyword', '', type=str)
    if not keyword:
        return AjaxResponse.from_error(msg="搜索关键词不能为空")
    users = FriendService.search_users(keyword)
    return AjaxResponse.from_success(data=users)


@reg.api.route('/friend/request', methods=['POST'])
@PreAuthorize(HasPerm("friend:add"))
@JsonSerializer()
def send_friend_request():
    """
    发送好友申请
    """
    data = request.get_json()
    to_user_id = data.get('to_user_id')
    message = data.get('message', '请求添加您为好友')
    if not to_user_id:
        return AjaxResponse.from_error(msg="被申请人ID不能为空")
    request_id = FriendService.send_friend_request(to_user_id, message)
    return AjaxResponse.from_success(data={"request_id": request_id})


@reg.api.route('/friend/requests', methods=['GET'])
@PreAuthorize(HasPerm("friend:list"))
@JsonSerializer()
def get_pending_requests():
    """
    获取待处理的申请列表
    """
    requests = FriendService.get_pending_requests()
    return AjaxResponse.from_success(data=requests)


@reg.api.route('/friend/request/<int:id>', methods=['PUT'])
@PreAuthorize(HasPerm("friend:edit"))
@JsonSerializer()
def handle_friend_request(id):
    """
    处理申请
    """
    data = request.get_json()
    status = data.get('status')
    if status not in [1, 2]:
        return AjaxResponse.from_error(msg="状态参数错误，1-同意，2-拒绝")
    success = FriendService.handle_friend_request(id, status)
    if success:
        return AjaxResponse.from_success(msg="处理成功")
    else:
        return AjaxResponse.from_error(msg="处理失败")


@reg.api.route('/friend/list', methods=['GET'])
@PreAuthorize(HasPerm("friend:list"))
@JsonSerializer()
def get_friend_list():
    """
    获取好友列表
    """
    friends = FriendService.get_friend_list()
    return AjaxResponse.from_success(data=friends)


@reg.api.route('/friend/<int:friendId>', methods=['DELETE'])
@PreAuthorize(HasPerm("friend:remove"))
@JsonSerializer()
def delete_friend(friendId):
    """
    删除好友
    """
    success = FriendService.delete_friend(friendId)
    if success:
        return AjaxResponse.from_success(msg="删除成功")
    else:
        return AjaxResponse.from_error(msg="删除失败")


@reg.api.route('/friend/public-key/<int:friendId>', methods=['GET'])
@PreAuthorize(HasPerm("friend:query"))
@JsonSerializer()
def get_friend_public_key(friendId):
    """
    获取好友公钥
    """
    public_key = FriendService.get_friend_public_key(friendId)
    if public_key:
        return AjaxResponse.from_success(data={"public_key": public_key})
    else:
        return AjaxResponse.from_error(msg="好友公钥不存在")
