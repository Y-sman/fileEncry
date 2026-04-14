# -*- coding: utf-8 -*-
# @Author  : balabala

import io
import logging

from flask import request, send_file
from flask_login import login_required

from owl_common.base.model import AjaxResponse
from owl_common.descriptor.serializer import JsonSerializer
from owl_common.exception import ServiceException
from owl_encry.service.enc_file import EncFileService
from service.file_share_service import FileShareService

logger = logging.getLogger(__name__)

try:
    from .. import reg
except ImportError:
    import sys
    owl_encry = sys.modules.get('owl_encry')
    if owl_encry and hasattr(owl_encry, 'reg'):
        reg = owl_encry.reg
    else:
        raise


@reg.api.route('/encry/file/share', methods=['POST'])
@login_required
@JsonSerializer()
def share_file():
    """分享文件。"""
    data = request.get_json()
    file_id = data.get('file_id')
    target_user_id = data.get('target_user_id')

    logger.info(f"分享文件请求: file_id={file_id}, target_user_id={target_user_id}")

    if not file_id:
        return AjaxResponse.from_error(msg="文件ID不能为空")
    if not target_user_id:
        return AjaxResponse.from_error(msg="目标用户ID不能为空")

    try:
        share_id = EncFileService.share_file_to_user(file_id, target_user_id)
        return AjaxResponse.from_success(data={"share_id": share_id})
    except Exception as e:
        logger.error(f"文件分享失败: {str(e)}")
        return AjaxResponse.from_error(msg=str(e))


@reg.api.route('/encry/file/shared-to-me', methods=['GET'])
@login_required
@JsonSerializer()
def shared_to_me():
    """分享给我的文件列表。"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    try:
        result = FileShareService.get_shared_to_me(page, page_size)
        return AjaxResponse.from_success(data=result)
    except Exception as e:
        logger.error(f"获取分享给我的文件列表失败: {str(e)}")
        return AjaxResponse.from_error(msg=str(e))


@reg.api.route('/encry/file/shared-by-me', methods=['GET'])
@login_required
@JsonSerializer()
def shared_by_me():
    """我分享的文件列表。"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    try:
        result = FileShareService.get_shared_by_me(page, page_size)
        return AjaxResponse.from_success(data=result)
    except Exception as e:
        logger.error(f"获取我分享的文件列表失败: {str(e)}")
        return AjaxResponse.from_error(msg=str(e))


@reg.api.route('/encry/file/share/<int:share_id>', methods=['DELETE'])
@login_required
@JsonSerializer()
def revoke_share(share_id):
    """撤销分享。"""
    try:
        success = FileShareService.revoke_share(share_id)
        if success:
            return AjaxResponse.from_success(msg="撤销分享成功")
        return AjaxResponse.from_error(msg="撤销分享失败")
    except Exception as e:
        logger.error(f"撤销分享异常: share_id={share_id}, error={str(e)}")
        return AjaxResponse.from_error(msg=str(e))


@reg.api.route('/encry/file/share/download/<int:share_id>', methods=['GET'])
@login_required
def download_shared_file(share_id):
    """按 share_id 下载分享文件。"""
    try:
        file_data, file_name = FileShareService.download_shared_file(share_id)
        return send_file(
            io.BytesIO(file_data),
            as_attachment=True,
            download_name=file_name,
            mimetype='application/octet-stream',
            conditional=False
        )
    except ServiceException as e:
        logger.error(f"文件下载失败(ServiceException): share_id={share_id}, error={str(e)}")
        from flask import jsonify
        return jsonify({'code': 500, 'msg': str(e)}), 500
    except Exception as e:
        logger.error(f"文件下载失败(Exception): share_id={share_id}, error={str(e)}")
        from flask import jsonify
        return jsonify({'code': 500, 'msg': str(e)}), 500


@reg.api.route('/encry/file/share/download/by-file/<int:file_id>', methods=['GET'])
@login_required
def download_shared_file_by_file_id(file_id):
    """按 file_id 下载当前用户收到的分享文件。"""
    try:
        file_data, file_name = FileShareService.download_shared_file_by_file_id(file_id)
        return send_file(
            io.BytesIO(file_data),
            as_attachment=True,
            download_name=file_name,
            mimetype='application/octet-stream',
            conditional=False
        )
    except ServiceException as e:
        logger.error(f"文件下载失败(ServiceException): file_id={file_id}, error={str(e)}")
        from flask import jsonify
        return jsonify({'code': 500, 'msg': str(e)}), 500
    except Exception as e:
        logger.error(f"文件下载失败(Exception): file_id={file_id}, error={str(e)}")
        from flask import jsonify
        return jsonify({'code': 500, 'msg': str(e)}), 500
