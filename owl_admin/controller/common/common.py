# -*- coding: utf-8 -*-
# @Author  : balabala

import os
import time
from flask import request, send_from_directory
from pydantic import Field
from typing_extensions import Annotated
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotFound

from owl_common.config import OWLConfig
from owl_common.constant import Constants
from owl_common.descriptor.serializer import JsonSerializer
from owl_common.descriptor.validator import FileValidator, QueryValidator
from owl_common.base.model import AjaxResponse, MultiFile
from owl_common.utils import FileUploadUtil, FileUtil, StringUtil
from ... import reg


@reg.api.route('/common/download')
@QueryValidator()
@JsonSerializer()
def common_download(
    file_name:Annotated[str,Field(min_length=1,max_length=100)],
    delete:Annotated[bool,Field(annotations=bool,default=False)],
):
    config = OWLConfig()
    file_path = config.download_path + file_name
    download_name = time.time() * 1000 + file_name[file_name.index("_") + 1:]
    try:
        response = send_from_directory(
            directory=config.download_path,
            path=file_name,
            as_attachment=True,
            download_name=download_name,
        )
        if delete:
            FileUtil.delete_file(file_path)
    except NotFound as e:
        return AjaxResponse.from_error("文件不存在")
    except Exception as e:
        return AjaxResponse.from_error("下载失败")
    return response


@reg.api.route('/common/upload', methods=['POST'])
@FileValidator()
@JsonSerializer()
def common_upload(file:MultiFile):
    file:FileStorage = file.one()
    config = OWLConfig()
    file_name = FileUploadUtil.upload(file, config.upload_path)
    url = request.host_url[:-1] + file_name
    new_file_name = FileUploadUtil.get_filename(file_name)
    original_filename = file.filename
    ajax_response = AjaxResponse.from_success()
    setattr(ajax_response,"url",url)
    setattr(ajax_response,"file_name",file_name)
    setattr(ajax_response,"new_file_name",new_file_name)
    setattr(ajax_response,"original_filename",original_filename)
    return ajax_response


@reg.api.route('/common/uploads', methods=['POST'])
@FileValidator()
@JsonSerializer()
def common_uploads(files:MultiFile):
    file_names = []
    urls = []
    new_file_names = []
    original_filenames = []
    config = OWLConfig()
    for _,file in files.items():
        file_name = FileUploadUtil.upload(file, config.upload_path)
        file_names.append(file_name)
        url = request.host_url[:-1] + file_name
        urls.append(url)
        new_file_name = FileUploadUtil.get_filename(file_name)
        new_file_names.append(new_file_name)
        original_filename = file.filename
        original_filenames.append(original_filename)
    ajax_response = AjaxResponse.from_success()
    setattr(ajax_response,"urls",urls.join(","))
    setattr(ajax_response,"file_names",file_names.join(","))
    setattr(ajax_response,"new_file_names",new_file_names.join(","))
    setattr(ajax_response,"original_filenames",original_filenames.join(","))
    return ajax_response


@reg.api.route('/common/download/resource')
@QueryValidator()
@JsonSerializer()
def common_download_resource(
    resource:Annotated[str,Field(annotation=str,min_length=1,max_length=100)]
):
    config = OWLConfig()
    download_path = config.download_path + StringUtil.substring_after(resource,Constants.RESOURCE_PREFIX)
    download_name = os.path.basename(download_path)
    try:
        response = send_from_directory(
            directory=config.download_path,
            path=download_path,
            as_attachment=True,
            download_name=download_name,
            )
    except NotFound as e:
        return AjaxResponse.from_error("文件不存在")
    except Exception as e:
        return AjaxResponse.from_error("下载失败")
    return response


@reg.api.route('/profile/<path:filename>')
def profile_static(filename):
    """
    提供静态资源访问，将 /profile/* 映射到实际的文件路径
    例如：/profile/upload/20251116/xxx.jpg -> D:/owl/uploadPath/upload/20251116/xxx.jpg
    """
    config = OWLConfig()
    try:
        # 解析路径，确定是 upload/download/avatar/import 中的哪个
        path_parts = filename.split('/', 1)
        if len(path_parts) < 1:
            raise NotFound()
        
        sub_dir = path_parts[0]  # upload/download/avatar/import
        file_subpath = path_parts[1] if len(path_parts) > 1 else ""
        
        # 根据子目录确定实际文件路径
        if sub_dir == "upload":
            directory = config.upload_path
        elif sub_dir == "download":
            directory = config.download_path
        elif sub_dir == "avatar":
            directory = config.avatar_path
        elif sub_dir == "import":
            directory = config.import_path
        else:
            raise NotFound()
        
        # 检查文件是否存在
        file_path = os.path.join(directory, file_subpath)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise NotFound()
        
        # 发送文件
        return send_from_directory(
            directory=directory,
            path=file_subpath,
            as_attachment=False
        )
    except NotFound:
        return NotFound(description="文件不存在")
    except Exception as e:
        return NotFound(description=f"文件访问失败: {str(e)}")
