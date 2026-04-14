# -*- coding: utf-8 -*-
# @Author  : balabala

from owl_common.base.model import AjaxResponse, TableResponse
from owl_common.descriptor.serializer import JsonSerializer
from owl_common.descriptor.validator import QueryValidator, PathValidator, BodyValidator
from owl_framework.descriptor.permission import HasPerm, PreAuthorize
from owl_framework.descriptor.log import Log
from owl_common.domain.enum import BusinessType
from ... import reg


@reg.api.route("/tool/gen/list", methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("tool:gen:list"))
@JsonSerializer()
def tool_gen_list(dto=None):
    """
    查询生成表数据列表
    注意：代码生成器功能暂未实现，返回空列表
    """
    # TODO: 实现代码生成器功能
    # 目前返回空列表，避免前端报错
    table_response = TableResponse(rows=[], total=0)
    return table_response


@reg.api.route("/tool/gen/db/list", methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("tool:gen:list"))
@JsonSerializer()
def tool_gen_db_list(dto=None):
    """
    查询数据库表列表
    注意：代码生成器功能暂未实现，返回空列表
    """
    # TODO: 实现代码生成器功能
    table_response = TableResponse(rows=[], total=0)
    return table_response


@reg.api.route("/tool/gen/<int:table_id>", methods=["GET"])
@PathValidator()
@PreAuthorize(HasPerm("tool:gen:query"))
@JsonSerializer()
def tool_gen_get(table_id: int):
    """
    查询表详细信息
    注意：代码生成器功能暂未实现
    """
    return AjaxResponse.from_error("代码生成器功能暂未实现")


@reg.api.route("/tool/gen", methods=["PUT"])
@BodyValidator()
@PreAuthorize(HasPerm("tool:gen:edit"))
@Log(title="代码生成", business_type=BusinessType.UPDATE)
@JsonSerializer()
def tool_gen_update(dto=None):
    """
    修改代码生成信息
    注意：代码生成器功能暂未实现
    """
    return AjaxResponse.from_error("代码生成器功能暂未实现")


@reg.api.route("/tool/gen/importTable", methods=["POST"])
@BodyValidator()
@PreAuthorize(HasPerm("tool:gen:import"))
@Log(title="代码生成", business_type=BusinessType.INSERT)
@JsonSerializer()
def tool_gen_import_table(dto=None):
    """
    导入表
    注意：代码生成器功能暂未实现
    """
    return AjaxResponse.from_error("代码生成器功能暂未实现")


@reg.api.route("/tool/gen/preview/<int:table_id>", methods=["GET"])
@PathValidator()
@PreAuthorize(HasPerm("tool:gen:preview"))
@JsonSerializer()
def tool_gen_preview(table_id: int):
    """
    预览生成代码
    注意：代码生成器功能暂未实现
    """
    return AjaxResponse.from_error("代码生成器功能暂未实现")


@reg.api.route("/tool/gen/<string:table_ids>", methods=["DELETE"])
@PathValidator()
@PreAuthorize(HasPerm("tool:gen:remove"))
@Log(title="代码生成", business_type=BusinessType.DELETE)
@JsonSerializer()
def tool_gen_delete(table_ids: str):
    """
    删除表数据（支持批量删除，ID用逗号分隔）
    注意：代码生成器功能暂未实现
    """
    return AjaxResponse.from_error("代码生成器功能暂未实现")


@reg.api.route("/tool/gen/genCode/<string:table_name>", methods=["GET"])
@PathValidator()
@PreAuthorize(HasPerm("tool:gen:code"))
@Log(title="代码生成", business_type=BusinessType.OTHER)
@JsonSerializer()
def tool_gen_gen_code(table_name: str):
    """
    生成代码（自定义路径）
    注意：代码生成器功能暂未实现
    """
    return AjaxResponse.from_error("代码生成器功能暂未实现")


@reg.api.route("/tool/gen/synchDb/<string:table_name>", methods=["GET"])
@PathValidator()
@PreAuthorize(HasPerm("tool:gen:edit"))
@Log(title="代码生成", business_type=BusinessType.UPDATE)
@JsonSerializer()
def tool_gen_synch_db(table_name: str):
    """
    同步数据库
    注意：代码生成器功能暂未实现
    """
    return AjaxResponse.from_error("代码生成器功能暂未实现")


@reg.api.route("/tool/gen/batchGenCode", methods=["GET"])
@QueryValidator()
@PreAuthorize(HasPerm("tool:gen:code"))
@Log(title="代码生成", business_type=BusinessType.OTHER)
@JsonSerializer()
def tool_gen_batch_gen_code(dto=None):
    """
    批量生成代码
    注意：代码生成器功能暂未实现
    """
    return AjaxResponse.from_error("代码生成器功能暂未实现")

