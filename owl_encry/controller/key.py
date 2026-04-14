# -*- coding: utf-8 -*-
# @Author  : balabala

from pydantic import Field
from typing_extensions import Annotated

from owl_common.base.model import AjaxResponse
from owl_common.descriptor.serializer import JsonSerializer
from owl_common.descriptor.validator import BodyValidator, PathValidator
from owl_common.domain.enum import BusinessType
from owl_common.utils import security_util
from owl_encry.service.enc_user_key import EncUserKeyService
from owl_framework.descriptor.log import Log
from owl_framework.descriptor.permission import HasPerm, PreAuthorize
from .. import reg


@reg.api.route("/encry/key/info", methods=["GET"])
@PreAuthorize(HasPerm("encry:key:query"))
@JsonSerializer()
def encry_key_info():
    """获取当前登录用户的密钥信息（不含私钥，仅本人可见）"""
    user_id = security_util.get_user_id()
    key = EncUserKeyService.select_by_user_id(user_id)
    ajax = AjaxResponse.from_success()
    if key:
        data = key.model_dump(exclude={'private_key_enc'}, by_alias=True)
        setattr(ajax, "data", data)
    else:
        setattr(ajax, "data", None)
    return ajax


@reg.api.route("/encry/key/generate", methods=["POST"])
@BodyValidator()
@PreAuthorize(HasPerm("encry:key:add"))
@Log(title="密钥管理", business_type=BusinessType.INSERT)
@JsonSerializer()
def encry_key_generate(
    keySize: Annotated[int, Field(default=2048, description='密钥长度')] = 2048
):
    """生成RSA密钥对"""
    user_id = security_util.get_user_id()
    key = EncUserKeyService.generate_key(user_id, keySize)
    ajax = AjaxResponse.from_success(msg="密钥生成成功")
    setattr(ajax, "data", key.model_dump(exclude={'private_key_enc'}, by_alias=True))
    return ajax


@reg.api.route("/encry/key/export/public", methods=["GET"])
@PreAuthorize(HasPerm("encry:key:export"))
@JsonSerializer()
def encry_key_export_public():
    """导出公钥"""
    user_id = security_util.get_user_id()
    public_key = EncUserKeyService.export_public_key(user_id)
    ajax = AjaxResponse.from_success()
    setattr(ajax, "data", {"publicKey": public_key})
    return ajax


@reg.api.route("/encry/key/export/private", methods=["GET"])
@PreAuthorize(HasPerm("encry:key:export"))
@JsonSerializer()
def encry_key_export_private():
    """导出私钥（请妥善保管）"""
    user_id = security_util.get_user_id()
    private_key = EncUserKeyService.export_private_key(user_id)
    ajax = AjaxResponse.from_success()
    setattr(ajax, "data", {"privateKey": private_key})
    return ajax


@reg.api.route("/encry/key/public/<int:user_id>", methods=["GET"])
@JsonSerializer()
def encry_key_get_public(user_id):
    """获取指定用户的公钥"""
    public_key = EncUserKeyService.get_public_key_pem(user_id)
    if not public_key:
        return AjaxResponse.from_error(msg="用户未生成密钥")
    ajax = AjaxResponse.from_success()
    setattr(ajax, "data", {"publicKey": public_key})
    return ajax
