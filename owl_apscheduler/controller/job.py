# -*- coding: utf-8 -*-
# @Author  : balabala

from typing import List
from typing_extensions import Annotated
from pydantic import BeforeValidator

from owl_apscheduler.domain.entity import SysJob
from owl_apscheduler.service.job import SysJobService
from owl_apscheduler.util import ScheduleUtil
from owl_common.base.model import AjaxResponse, TableResponse
from owl_common.base.transformer import ids_to_list
from owl_common.constant import Constants
from owl_common.descriptor.serializer import JsonSerializer
from owl_common.descriptor.validator import BodyValidator, QueryValidator, PathValidator
from owl_common.domain.enum import BusinessType
from owl_common.utils import security_util as SecurityUtil
from owl_framework.descriptor.log import Log
from owl_framework.descriptor.permission import HasPerm, PreAuthorize
from owl_system.mapper.sys_config import SysConfigMapper
from .. import reg


@reg.api.route("/monitor/job/list", methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("monitor:job:list"))
@JsonSerializer()
def common_job_list(dto:SysJob) -> TableResponse:
    """
    获取定时任务列表
    
    Args:
        dto(SysJob): 查询条件

    Returns:
        TableResponse: 数据响应
    """
    rows: List[SysJob] = SysJobService.select_job_list(dto)
    table_response = TableResponse(rows=rows)
    return table_response


@reg.api.route("/monitor/job/export", methods=["POST"])
@BodyValidator()
@PreAuthorize(HasPerm("monitor:job:export"))
@Log(title="定时任务",business_type=BusinessType.EXPORT)
@JsonSerializer()
def common_job_export(dto:SysJob):
    """
    导出定时任务列表

    Args:
        dto(SysJob): 查询条件

    Returns:
        _type_: 数据响应
    """
    # todo
    rows: List[SysJob] = SysJobService.select_job_list(dto)
    return "Hello, World!"


@reg.api.route("/monitor/job/whitelist", methods=["GET"])
@PreAuthorize(HasPerm("monitor:job:query"))
@JsonSerializer()
def common_job_whitelist() -> AjaxResponse:
    """
    获取定时任务白名单配置
    
    Returns:
        AjaxResponse: 白名单配置信息
    """
    from owl_system.service.sys_config import SysConfigService
    whitelist_config = SysConfigService.select_config_by_key("monitor.job.whitelist")
    if whitelist_config:
        # 解析白名单配置（逗号分隔）
        whitelist_strs = [s.strip() for s in whitelist_config.split(",") if s.strip()]
    else:
        # 使用默认白名单
        from owl_apscheduler.constant import ScheduleConstant
        whitelist_strs = list(ScheduleConstant.JOB_WHITELIST_STR)
    
    return AjaxResponse.from_success(data={
        "whitelist": whitelist_strs,
        "whitelistStr": whitelist_config or ",".join(whitelist_strs)
    })


@reg.api.route("/monitor/job/whitelist", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm("monitor:job:edit"))
@Log(title="定时任务",business_type=BusinessType.UPDATE)
@JsonSerializer()
def common_job_whitelist_update() -> AjaxResponse:
    """
    更新定时任务白名单配置
    
    Returns:
        AjaxResponse: 操作结果
    """
    from flask import request
    from owl_system.service.sys_config import SysConfigService
    from owl_system.domain.entity import SysConfig
    
    data = request.get_json()
    whitelist_str = data.get("whitelistStr", "").strip() if data else ""
    
    # 查找或创建配置
    config = SysConfig(config_key="monitor.job.whitelist")
    existing_config = SysConfigMapper.select_config(config)
    
    if existing_config:
        # 更新现有配置
        existing_config.config_value = whitelist_str
        existing_config.config_name = "定时任务白名单"
        existing_config.update_by_user(SecurityUtil.get_username())
        flag = SysConfigService.update_config(existing_config)
    else:
        # 创建新配置
        new_config = SysConfig()
        new_config.config_name = "定时任务白名单"
        new_config.config_key = "monitor.job.whitelist"
        new_config.config_value = whitelist_str
        new_config.config_type = "N"  # 非系统内置
        new_config.create_by_user(SecurityUtil.get_username())
        SysConfigService.insert_config(new_config)
        flag = True
    
    # 清除缓存
    if flag:
        SysConfigService.reset_config_cache()
    
    return AjaxResponse.from_success() if flag else AjaxResponse.from_error()


@reg.api.route("/monitor/job/<int:id>", methods=["GET"])
@PathValidator()
@PreAuthorize(HasPerm("monitor:job:query"))
@JsonSerializer()
def common_job_detail(id: int) -> AjaxResponse:
    """
    获取定时任务详情

    Args:
        id (int): 任务ID

    Returns:
        AjaxResponse: 数据响应
    """
    job: SysJob = SysJobService.select_job_by_id(id)
    return AjaxResponse.from_success(data=job)


@reg.api.route("/monitor/job", methods=["POST"])
@BodyValidator()
@PreAuthorize(HasPerm("monitor:job:add"))
@Log(title="定时任务",business_type=BusinessType.INSERT)
@JsonSerializer()
def common_job_add(dto:SysJob) -> AjaxResponse:
    """
    新增定时任务

    Args:
        dto (SysJob): 任务信息

    Returns:
        AjaxResponse: 数据响应
    """
    if not ScheduleUtil.check_cron_expression(dto.cron_expression):
        return AjaxResponse.from_error(f"新增任务{dto.job_name}失败，cron表达式格式错误")
    for forbid_word in [
        Constants.LOOKUP_LDAP,
        Constants.LOOKUP_LDAPS,
        Constants.LOOKUP_RMI,
        Constants.HTTP,
        Constants.HTTPS
    ]:
        if forbid_word.lower() in dto.invoke_target.lower():
            return AjaxResponse.from_error(f"新增任务{dto.job_name}失败，调用目标中包含非法字符{forbid_word}")
    if not ScheduleUtil.white_list_check(dto.invoke_target):
        return AjaxResponse.from_error(f"新增任务{dto.job_name}失败，目标字符串不在白名单中")
    dto.create_by_user(SecurityUtil.get_username())
    flag = SysJobService.insert_job(dto)
    return AjaxResponse.from_success() if flag else AjaxResponse.from_error()


@reg.api.route("/monitor/job", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm("monitor:job:edit"))
@Log(title="定时任务",business_type=BusinessType.UPDATE)
@JsonSerializer()
def common_job_edit(dto:SysJob) -> AjaxResponse:
    """
    修改定时任务

    Args:
        dto (SysJob): 任务信息

    Returns:
        AjaxResponse: 数据响应
    """
    if not dto.cron_expression or not ScheduleUtil.check_cron_expression(dto.cron_expression):
        return AjaxResponse.from_error(f"修改任务{dto.job_name or '未知'}失败，cron表达式格式错误")
    if not dto.invoke_target:
        return AjaxResponse.from_error(f"修改任务{dto.job_name or '未知'}失败，调用目标不能为空")
    for forbid_word in [
        Constants.LOOKUP_LDAP,
        Constants.LOOKUP_LDAPS,
        Constants.LOOKUP_RMI,
        Constants.HTTP,
        Constants.HTTPS
    ]:
        if forbid_word.lower() in dto.invoke_target.lower():
            return AjaxResponse.from_error(f"修改任务{dto.job_name or '未知'}失败，调用目标中包含非法字符{forbid_word}")
    if not ScheduleUtil.white_list_check(dto.invoke_target):
        return AjaxResponse.from_error(f"修改任务{dto.job_name or '未知'}失败，目标字符串不在白名单中")
    dto.update_by_user(SecurityUtil.get_username())
    flag = SysJobService.update_job(dto)
    return AjaxResponse.from_success() if flag else AjaxResponse.from_error()


@reg.api.route("/monitor/job/changeStatus", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm('monitor:job:changeStatus'))
@Log(title = "定时任务", business_type = BusinessType.UPDATE)
@JsonSerializer()
def common_job_status_edit(dto:SysJob) -> AjaxResponse:
    """
    修改定时任务状态

    Args:
        dto (SysJob): 任务实体

    Returns:
        AjaxResponse: 数据响应
    """
    job: SysJob = SysJobService.select_job_by_id(dto.job_id)
    job.status = dto.status
    flag = SysJobService.change_job_status(job)
    dto.update_by_user(SecurityUtil.get_username())
    return AjaxResponse.from_success() if flag else AjaxResponse.from_error()


@reg.api.route("/monitor/job/run", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm('monitor:job:changeStatus'))
@Log(title = "定时任务", business_type = BusinessType.UPDATE)
@JsonSerializer()
def common_job_run(dto:SysJob) -> AjaxResponse:
    """
    立即执行定时任务

    Args:
        dto (SysJob): 任务实体

    Returns:
        AjaxResponse: 数据响应
    """
    SysJobService.run(dto)
    return AjaxResponse.from_success()


@reg.api.route("/monitor/job/remove", methods=["DELETE"])
@PathValidator()
@PreAuthorize(HasPerm('monitor:job:remove'))
@Log(title = "定时任务", business_type = BusinessType.DELETE)
@JsonSerializer()
def common_job_remove(
    ids: Annotated[List[int],BeforeValidator(ids_to_list)]
) -> AjaxResponse:
    """
    删除定时任务

    Args:
        ids (List[int]): 任务ID列表

    Returns:
        AjaxResponse: 数据响应
    """
    SysJobService.delete_job_by_ids(ids)
    return AjaxResponse.from_success()
