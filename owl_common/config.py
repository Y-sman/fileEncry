# -*- coding: utf-8 -*-
# @Author  : balabala

import os
from owl_common.owl.config import CONFIG_CACHE
        

class OWLConfig:
    
    profile = CONFIG_CACHE["owl.profile"]
    
    @property
    def upload_path(self) -> str:
        """
        获取上传路径
        profile 本身就是上传文件保存地址

        Returns:
            str: 上传路径
        """
        # profile 本身就是上传路径，直接使用
        return os.path.join(self.profile, "upload") if self.profile else "uploads/upload"
    
    @property
    def download_path(self) -> str:
        """
        获取下载路径

        Returns:
            str: 下载路径
        """
        # profile 本身就是上传路径，下载路径在其下
        return os.path.join(self.profile, "download") if self.profile else "uploads/download"
    
    @property
    def avatar_path(self) -> str:
        """
        获取头像路径

        Returns:
            str: 头像路径
        """
        # profile 本身就是上传路径，头像路径在其下
        return os.path.join(self.profile, "avatar") if self.profile else "uploads/avatar"
    
    @property
    def import_path(self) -> str:
        """
        获取导入路径

        Returns:
            str: 导入路径
        """
        # profile 本身就是上传路径，导入路径在其下
        return os.path.join(self.profile, "import") if self.profile else "uploads/import"

    @property
    def encry_path(self) -> str:
        """
        获取加密文件存储路径

        Returns:
            str: 加密文件路径
        """
        # 使用相对路径替代绝对路径，避免权限问题
        return "uploads/encry"
    

