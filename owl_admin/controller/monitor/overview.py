# -*- coding: utf-8 -*-
# @Author  : balabala

from owl_common.base.model import AjaxResponse
from owl_common.descriptor.serializer import JsonSerializer
from owl_framework.descriptor.permission import HasPerm, PreAuthorize
from owl_system.mapper.sys_user import SysUserMapper
from ... import reg


@reg.api.route("/monitor/overview", methods=["GET"])
@PreAuthorize(HasPerm("monitor:server:list"))
@JsonSerializer()
def monitor_overview():
    """系统监控概览：用户总数、加密文件存储总量（字节）"""
    try:
        from owl_encry.mapper.enc_file import EncFileMapper
        user_count = SysUserMapper.count_all()
        total_storage = EncFileMapper.total_storage()
    except ImportError:
        user_count = SysUserMapper.count_all()
        total_storage = 0
    data = {"userCount": user_count, "totalStorage": total_storage}
    return AjaxResponse.from_success(data=data)
