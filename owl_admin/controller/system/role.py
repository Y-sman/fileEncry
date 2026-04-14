# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import Annotated, List
from pydantic import BeforeValidator, Field

from owl_common.constant import UserConstants
from owl_common.base.transformer import ids_to_list
from owl_common.base.model import AjaxResponse, TableResponse
from owl_common.domain.entity import SysRole
from owl_common.domain.enum import BusinessType
from owl_common.descriptor.serializer import BaseSerializer, JsonSerializer
from owl_common.descriptor.validator import BodyValidator, QueryValidator,PathValidator
from owl_common.utils import security_util as SecurityUtil
from owl_system.domain.entity import SysUserRole
from owl_system.service import SysRoleService,SysUserService
from owl_framework.descriptor.log import Log
from owl_framework.descriptor.permission import HasPerm, PreAuthorize
from ... import reg


@reg.api.route("/system/role/list", methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("system:role:list"))
@JsonSerializer()
def system_role_list(dto:SysRole):
    '''
        获取角色列表
    '''
    rows = SysRoleService.select_role_list(dto)
    return TableResponse(rows=rows)


@reg.api.route("/system/role/<int:id>", methods=["GET"])
@PathValidator()
@PreAuthorize(HasPerm("system:role:query"))
@JsonSerializer()
def system_role_detail(id:int):
    '''
        获取角色详情
    '''
    SysRoleService.check_role_data_scope(id)
    eo = SysRoleService.select_role_by_id(id)
    return AjaxResponse.from_success(data=eo) \
        if eo else AjaxResponse.from_error()


@reg.api.route("/system/role/export", methods=["POST"])
@BodyValidator()
@PreAuthorize(HasPerm("system:role:export"))
@Log(title="角色管理",business_type=BusinessType.EXPORT)
@BaseSerializer()
def system_role_export(dto:SysRole):
    '''
        导出角色
    '''
    # todo
    rows = SysRoleService.select_role_list(dto)
    table_response = TableResponse(rows=rows)
    return table_response


@reg.api.route("/system/role", methods=["POST"])
@BodyValidator()
@PreAuthorize(HasPerm("system:role:add"))
@Log(title="角色管理",business_type=BusinessType.INSERT)
@JsonSerializer()
def system_role_create(dto:SysRole):
    '''
        创建角色
    '''
    if UserConstants.NOT_UNIQUE == SysRoleService.check_role_name_unique(dto):
        return AjaxResponse.from_error(f"新增角色'{dto.role_name}'失败，角色名称已存在")
    elif UserConstants.NOT_UNIQUE == \
        SysRoleService.check_role_key_unique(dto):
        return AjaxResponse.from_error(f"新增角色'{dto.role_name}'失败，角色权限已存在")
    dto.create_by_user(SecurityUtil.get_username())
    SysRoleService.insert_role(dto)
    return AjaxResponse.from_success()


@reg.api.route("/system/role", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm("system:role:edit"))
@Log(title="角色管理",business_type=BusinessType.UPDATE)
@JsonSerializer()
def system_role_update(dto:SysRole):
    '''
        修改角色
    '''
    import logging
    logger = logging.getLogger(__name__)
    
    # 调试日志：打印接收到的数据
    logger.debug(f"修改角色 - 接收到的数据: role_id={dto.role_id}, role_name={dto.role_name}, menu_ids={dto.menu_ids}")
    
    SysRoleService.check_role_allowed(dto)
    SysRoleService.check_role_data_scope(dto.role_id)
    if UserConstants.NOT_UNIQUE == SysRoleService.check_role_name_unique(dto):
        return AjaxResponse.from_error(f"修改角色'{dto.role_name}'失败，角色名称已存在")
    elif UserConstants.NOT_UNIQUE == \
        SysRoleService.check_role_key_unique(dto):
        return AjaxResponse.from_error(f"修改角色'{dto.role_name}'失败，角色权限已存在")
    dto.update_by_user(SecurityUtil.get_username())
    
    # 调试日志：打印保存前的数据
    logger.debug(f"修改角色 - 保存前: role_id={dto.role_id}, menu_ids={dto.menu_ids}, type={type(dto.menu_ids)}")
    
    result = SysRoleService.update_role(dto)
    
    # 调试日志：打印保存结果
    logger.debug(f"修改角色 - 保存结果: {result}")
    
    return AjaxResponse.from_success()


@reg.api.route("/system/role/dataScope", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm("system:role:edit"))
@Log(title="角色管理",business_type=BusinessType.UPDATE)
@JsonSerializer()
def system_data_scope_update(dto:SysRole):
    '''
        修改数据权限
    '''
    SysRoleService.check_role_allowed(dto)
    SysRoleService.check_role_data_scope(dto.role_id)
    return AjaxResponse.from_success()


@reg.api.route("/system/role/changeStatus", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm("system:role:edit"))
@Log(title="角色管理",business_type=BusinessType.UPDATE)
@JsonSerializer()
def system_role_change_status(dto:SysRole):
    '''
        修改角色状态
    '''
    SysRoleService.check_role_allowed(dto)
    SysRoleService.check_role_data_scope(dto.role_id)
    flag = SysRoleService.update_role_status(dto)
    return AjaxResponse.from_success() if flag else AjaxResponse.from_error()


@reg.api.route("/system/role/<ids>", methods=["DELETE"])
@PathValidator()
@PreAuthorize(HasPerm("system:role:remove"))
@Log(title="角色管理",business_type=BusinessType.DELETE)
@JsonSerializer()
def system_role_delete(
    ids: Annotated[List[int],BeforeValidator(ids_to_list)]
):
    '''
        删除角色
    '''
    # Path 参数可能为字符串 "100"，未转列表时 for role_id in ids 会遍历到 "1" 被误判为超级管理员
    try:
        ids = ids_to_list(ids) if not isinstance(ids, list) else (ids or [])
    except (ValueError, TypeError):
        return AjaxResponse.from_error("角色ID格式无效")
    if not ids:
        return AjaxResponse.from_error("请选择要删除的角色")
    SysRoleService.delete_role_by_ids(ids)
    return AjaxResponse.from_success()


@reg.api.route("/system/role/optionselect", methods=["GET"])
@PreAuthorize(HasPerm("system:role:query"))
@JsonSerializer()
def system_role_options():
    '''
        获取角色选择框列表
    '''
    rows = SysRoleService.select_role_all()
    return AjaxResponse.from_success(data=rows)


@reg.api.route("/system/role/authUser/allocatedList", methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("system:role:list"))
@JsonSerializer()
def system_role_user_allocated_list(dto:SysRole):
    '''
        获取角色选择框列表
    '''
    rows = SysUserService.select_allocated_list(dto)
    return TableResponse(rows=rows)


@reg.api.route("/system/role/authUser/unallocatedList", methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("system:role:list"))
@JsonSerializer()
def system_role_user_unallocated_list(dto:SysRole):
    '''
        查询未分配用户角色列表
    '''
    rows = SysUserService.select_unallocated_list(dto)
    return TableResponse(rows=rows)


@reg.api.route("/system/role/authUser/cancel", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm("system:role:edit"))
@Log(title="角色管理",business_type=BusinessType.GRANT)
@JsonSerializer()
def system_role_user_cancel(dto:SysUserRole):
    '''
        取消授权用户
    '''
    flag = SysRoleService.delete_auth_user(dto)
    return AjaxResponse.from_success() if flag else AjaxResponse.from_error()


@reg.api.route("/system/role/authUser/cancelAll", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm("system:role:edit"))
@Log(title="角色管理",business_type=BusinessType.GRANT)
@JsonSerializer()
def system_role_user_cancel_all(
    role_id:Annotated[int,Field(gt=0)], 
    user_ids:Annotated[List[int],Field(default_factory=List)]
):
    '''
        批量取消授权用户
    '''
    flag = SysRoleService.delete_auth_users(
        role_id=role_id, 
        user_ids=user_ids
        )
    return AjaxResponse.from_success() if flag else AjaxResponse.from_error()


@reg.api.route("/system/role/authUser/selectAll", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm("system:role:edit"))
@Log(title="角色管理",business_type=BusinessType.GRANT)
@JsonSerializer()
def system_role_user_select_all(
    role_id:Annotated[int,Field(gt=0)], 
    user_ids:Annotated[List[int],Field(default_factory=List)]
):
    '''
        批量选择授权用户
    '''
    SysRoleService.check_role_data_scope(role_id)
    flag = SysRoleService.insert_auth_users(
        role_id=role_id, 
        user_ids=user_ids
        )
    return AjaxResponse.from_success() if flag else AjaxResponse.from_error()

