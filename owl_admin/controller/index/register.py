# -*- coding: utf-8 -*-
# @Author  : balabala

from owl_common.base.model import AjaxResponse
from owl_common.descriptor.serializer import JsonSerializer
from owl_common.descriptor.validator import BodyValidator
from owl_common.domain.vo import RegisterBody
from owl_system.service import SysConfigService
from owl_framework.service.sys_register import RegisterService
from ... import reg


@reg.api.route("/register", methods=["POST"])
@BodyValidator()
@JsonSerializer()
def index_register(dto: RegisterBody):
    '''
    注册接口
    '''
    value = SysConfigService.select_config_by_key("sys.account.registerUser")
    if value != "true":
        return AjaxResponse.from_error("当前系统没有开启注册功能！")
    msg = RegisterService.register(dto)
    if msg:
        return AjaxResponse.from_error(msg=msg)
    else:
        return AjaxResponse.from_success()
