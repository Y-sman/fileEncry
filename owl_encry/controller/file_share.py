# -*- coding: utf-8 -*-
# @Author  : balabala

from flask import request, send_file
from flask_login import login_required
import io
import logging

# 配置日志
logger = logging.getLogger(__name__)

from owl_common.descriptor.serializer import JsonSerializer
from owl_common.base.model import AjaxResponse
from owl_common.exception import ServiceException
from owl_encry.service.enc_file import EncFileService
from service.file_share_service import FileShareService

# 导入 reg，如果失败则尝试从 sys.modules 获取
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
    """
    分享文件
    """
    data = request.get_json()
    file_id = data.get('file_id')
    target_user_id = data.get('target_user_id')
    
    logger.info(f"分享文件请求: file_id={file_id}, target_user_id={target_user_id}")
    
    if not file_id:
        logger.warning("文件ID不能为空")
        return AjaxResponse.from_error(msg="文件ID不能为空")
    if not target_user_id:
        logger.warning("目标用户ID不能为空")
        return AjaxResponse.from_error(msg="目标用户ID不能为空")
    
    try:
        share_id = EncFileService.share_file_to_user(file_id, target_user_id)
        logger.info(f"文件分享成功: share_id={share_id}")
        return AjaxResponse.from_success(data={"share_id": share_id})
    except Exception as e:
        logger.error(f"文件分享失败: {str(e)}")
        return AjaxResponse.from_error(msg=str(e))


@reg.api.route('/encry/file/shared-to-me', methods=['GET'])
@login_required
@JsonSerializer()
def shared_to_me():
    """
    分享给我的文件列表
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    
    logger.info(f"获取分享给我的文件列表: page={page}, page_size={page_size}")
    
    try:
        result = FileShareService.get_shared_to_me(page, page_size)
        logger.info(f"获取分享给我的文件列表成功: total={result.get('total')}")
        return AjaxResponse.from_success(data=result)
    except Exception as e:
        logger.error(f"获取分享给我的文件列表失败: {str(e)}")
        return AjaxResponse.from_error(msg=str(e))


@reg.api.route('/encry/file/shared-by-me', methods=['GET'])
@login_required
@JsonSerializer()
def shared_by_me():
    """
    我分享的文件列表
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    
    logger.info(f"获取我分享的文件列表: page={page}, page_size={page_size}")
    
    try:
        result = FileShareService.get_shared_by_me(page, page_size)
        logger.info(f"获取我分享的文件列表成功: total={result.get('total')}")
        return AjaxResponse.from_success(data=result)
    except Exception as e:
        logger.error(f"获取我分享的文件列表失败: {str(e)}")
        return AjaxResponse.from_error(msg=str(e))


@reg.api.route('/encry/file/share/<int:share_id>', methods=['DELETE'])
@login_required
@JsonSerializer()
def revoke_share(share_id):
    """
    撤销分享
    """
    logger.info(f"撤销分享请求: share_id={share_id}")
    
    try:
        success = FileShareService.revoke_share(share_id)
        if success:
            logger.info(f"撤销分享成功: share_id={share_id}")
            return AjaxResponse.from_success(msg="撤销分享成功")
        else:
            logger.warning(f"撤销分享失败: share_id={share_id}")
            return AjaxResponse.from_error(msg="撤销分享失败")
    except Exception as e:
        logger.error(f"撤销分享异常: share_id={share_id}, error={str(e)}")
        return AjaxResponse.from_error(msg=str(e))


@reg.api.route('/encry/file/share/download/<int:share_id>', methods=['GET'])
@login_required
def download_shared_file(share_id):
    """
    下载分享的文件
    """
    logger.info(f"下载分享文件请求: {share_id}")
    
    try:
        logger.info(f"开始调用 FileShareService.download_shared_file: {share_id}")
        file_data, file_name = FileShareService.download_shared_file(share_id)
        logger.info(f"文件下载成功: share_id={share_id}, file_name={file_name}, size={len(file_data)} bytes")
        
        # 创建文件流
        file_stream = io.BytesIO(file_data)
        
        # 返回文件下载
        logger.info(f"返回文件下载: {file_name}")
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=file_name,
            mimetype='application/octet-stream'
        )
    except ServiceException as e:
        logger.error(f"文件下载失败 (ServiceException): share_id={share_id}, error={str(e)}")
        # 返回 JSON 错误响应
        from flask import jsonify
        return jsonify({'code': 500, 'msg': str(e)}), 500
    except Exception as e:
        logger.error(f"文件下载失败 (Exception): share_id={share_id}, error={str(e)}")
        # 返回 JSON 错误响应
        from flask import jsonify
        return jsonify({'code': 500, 'msg': str(e)}), 500
