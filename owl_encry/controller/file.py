# -*- coding: utf-8 -*-
# @Author  : balabala

from flask import request, send_file
from io import BytesIO

from owl_common.base.transformer import ids_to_list
from owl_common.base.model import AjaxResponse, TableResponse, MultiFile
from owl_common.descriptor.serializer import JsonSerializer
from owl_common.descriptor.validator import FileValidator, QueryValidator, PathValidator
from owl_common.domain.enum import BusinessType
from owl_common.utils import security_util
from owl_encry.domain.entity import EncFile
from owl_encry.service.enc_file import EncFileService
from owl_framework.descriptor.log import Log
from owl_framework.descriptor.permission import HasPerm, PreAuthorize
from .. import reg


@reg.api.route("/encry/file/stats", methods=["GET"])
@PreAuthorize(HasPerm("encry:file:list"))
@JsonSerializer()
def encry_file_stats():
    """个人中心使用统计：文件数量、存储空间（字节）"""
    user_id = security_util.get_user_id()
    stats = EncFileService.get_user_stats(user_id)
    ajax = AjaxResponse.from_success()
    setattr(ajax, "data", stats)
    return ajax


@reg.api.route("/encry/file/list", methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("encry:file:list"))
@JsonSerializer()
def encry_file_list(dto: EncFile):
    """获取加密文件列表（仅当前用户）"""
    dto.user_id = security_util.get_user_id()
    rows = EncFileService.select_list(dto)
    return TableResponse(rows=rows)


@reg.api.route("/encry/file/upload", methods=["POST"])
@FileValidator()
@PreAuthorize(HasPerm("encry:file:upload"))
@Log(title="加密文件", business_type=BusinessType.INSERT)
@JsonSerializer()
def encry_file_upload(file: MultiFile):
    """加密上传文件。支持表单：encryptAlgo(AES/DES)、aesMode(CBC/GCM/ECB)、userKey(可选)"""
    encrypt_algo = request.form.get('encryptAlgo') or request.form.get('encrypt_algo') or 'AES'
    aes_mode = request.form.get('aesMode') or request.form.get('aes_mode') or 'CBC'
    user_key = request.form.get('userKey') or request.form.get('user_key') or ''
    file_obj = file.one()
    enc_file = EncFileService.upload_encrypt(
        file_obj,
        encrypt_algo=encrypt_algo,
        aes_mode=aes_mode,
        user_sym_key=user_key.strip() or None,
    )
    ajax = AjaxResponse.from_success(msg="上传成功")
    setattr(ajax, "data", enc_file.model_dump(exclude={'sym_key_enc'}, by_alias=True))
    return ajax


@reg.api.route("/encry/file/hash/<int:file_id>", methods=["GET"])
@PathValidator()
@PreAuthorize(HasPerm("encry:file:query"))
@JsonSerializer()
def encry_file_hash(file_id: int):
    """获取加密文件的哈希值（用于完整性校验）"""
    enc_file = EncFileService.select_by_id(file_id, security_util.get_user_id())
    if not enc_file:
        from owl_common.exception import ServiceException
        raise ServiceException("文件不存在或无权访问")
    ajax = AjaxResponse.from_success()
    setattr(ajax, "data", {"fileHash": enc_file.file_hash or "", "originalName": enc_file.original_name})
    return ajax


@reg.api.route("/encry/file/download/<int:file_id>", methods=["GET"])
@PathValidator()
@PreAuthorize(HasPerm("encry:file:download"))
@Log(title="解密下载", business_type=BusinessType.EXPORT)
def encry_file_download(file_id: int):
    """解密下载文件，可选 verifyHash 参数进行完整性校验"""
    verify_hash = request.args.get('verifyHash') or request.args.get('verify_hash')
    decrypted, original_name = EncFileService.decrypt_download(file_id, verify_hash=verify_hash)
    return send_file(
        BytesIO(decrypted),
        as_attachment=True,
        download_name=original_name,
        mimetype='application/octet-stream',
        conditional=False  # 始终返回 200 与完整内容，避免 206 导致前端报错
    )


@reg.api.route("/encry/file/<int:file_id>", methods=["DELETE"])
@PathValidator()
@PreAuthorize(HasPerm("encry:file:remove"))
@Log(title="加密文件", business_type=BusinessType.DELETE)
@JsonSerializer()
def encry_file_remove(file_id: int):
    """删除加密文件"""
    EncFileService.delete_file(file_id)
    return AjaxResponse.from_success(msg="删除成功")


@reg.api.route("/encry/file/remove/<ids>", methods=["DELETE"])
@PathValidator()
@PreAuthorize(HasPerm("encry:file:remove"))
@Log(title="加密文件", business_type=BusinessType.DELETE)
@JsonSerializer()
def encry_file_remove_batch(ids: str):
    """批量删除加密文件"""
    file_ids = ids_to_list(ids)
    if not file_ids:
        return AjaxResponse.from_error("请选择要删除的文件")
    EncFileService.delete_files(file_ids)
    return AjaxResponse.from_success(msg="删除成功")


@reg.api.route("/encry/file/share/upload", methods=["POST"])
@FileValidator()
@JsonSerializer()
def encry_file_share_upload(file: MultiFile):
    """为分享而加密上传文件"""
    receiver_id = request.form.get('receiver_id')
    if not receiver_id:
        return AjaxResponse.from_error(msg="接收者ID不能为空")
    
    try:
        receiver_id = int(receiver_id)
    except ValueError:
        return AjaxResponse.from_error(msg="接收者ID必须是数字")
    
    file_obj = file.one()
    result = EncFileService.upload_for_share(file_obj, receiver_id)
    ajax = AjaxResponse.from_success(msg="文件加密发送成功")
    setattr(ajax, "data", result)
    return ajax
