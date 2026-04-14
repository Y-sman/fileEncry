# -*- coding: utf-8 -*-

from flask import flash

from owl_common.domain.vo import RegisterBody
from owl_common.utils import security_util as SecurityUtil
from owl_common.constant import Constants, UserConstants
from owl_common.exception import CaptchaException, CaptchaExpireException
from owl_common.domain.entity import SysUser
from owl_system.service import SysUserService
from owl_admin.ext import redis_cache

# todo

class RegisterService:

    @classmethod
    def register(cls, body:RegisterBody) -> str:
        """
        注册用户
        
        Args:
            body (RegisterBody): 注册信息
        
        Returns:
            str: 注册结果信息    
        """
        msg = ""
        username = (body.username or "").strip()
        email = (getattr(body, "email", None) or "").strip()
        password = body.password.get_secret_value() if body.password else ""

        if not username:
            msg = "用户名不能为空"
        elif not email:
            msg = "邮箱不能为空"
        elif not password:
            msg = "密码不能为空"
        elif len(username) < UserConstants.USERNAME_MIN_LENGTH or len(username) > UserConstants.USERNAME_MAX_LENGTH:
            msg = "用户名长度须在 2～20 之间"
        elif len(password) < UserConstants.PASSWORD_MIN_LENGTH or len(password) > UserConstants.PASSWORD_MAX_LENGTH:
            msg = "密码长度须在 5～20 之间"
        else:
            ok, err = SecurityUtil.validate_password_strength(password, min_length=8)
            if not ok:
                msg = err
            elif UserConstants.NOT_UNIQUE == SysUserService.check_user_name_unique(SysUser(user_name=username)):
                msg = f"用户名 '{username}' 已存在"
            elif email and UserConstants.NOT_UNIQUE == SysUserService.check_email_unique(SysUser(email=email)):
                msg = f"邮箱 '{email}' 已被注册"
            else:
                enc = SecurityUtil.encrypt_password(password)
                pwd = enc.decode("utf-8") if isinstance(enc, bytes) else enc
                sys_user = SysUser(
                    user_name=username,
                    nick_name=username,
                    email=email or None,
                    password=pwd,
                    dept_id=100,
                    role_ids=[2]
                )
                reg_flag = SysUserService.register_user(sys_user)
                if not reg_flag:
                    msg = "注册失败，请联系管理员"
                else:
                    flash("user.register.success")
        return msg
    
    @classmethod
    def validate_captcha(self, username:str, code:str, uuid:str):
        """
        验证码校验
        
        Args:
            username (str): 用户名
            code (str): 验证码
            uuid (str): 验证码唯一标识
        
        Raises:
            CaptchaException: 验证码错误
            CaptchaExpireException: 验证码过期
        """
        verify_key = Constants.CAPTCHA_CODE_KEY + (uuid if uuid is not None else "")
        captcha = redis_cache.get_cache_object(verify_key)
        # redis_cache.delete_object(verify_key)
        if captcha is None:
            raise CaptchaExpireException()
        if code.lower() != captcha.lower():
            raise CaptchaException()