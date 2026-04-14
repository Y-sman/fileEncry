# -*- coding: utf-8 -*-
# @Author  : balabala

import bcrypt
from flask import abort
from flask_login import current_user
from owl_common.constant import HttpStatus
from owl_common.domain.entity import LoginUser
from owl_common.utils.base import UtilException


def get_user_id() -> int:
    """
    获取当前登录用户的ID

    Raises:
        UtilException: 获取用户ID异常

    Returns:
        int: 当前登录用户的ID 
    """
    try:
        return get_login_user().user_id
    except Exception:
        raise UtilException("获取用户ID异常", HttpStatus.UNAUTHORIZED)

def get_dept_id() -> int:
    """
    获取当前登录用户的部门ID

    Raises:
        UtilException: 获取部门ID异常

    Returns:
        int: 当前登录用户的部门ID 
    """
    try:
        return get_login_user().dept_id
    except Exception:
        raise UtilException("获取部门ID异常", HttpStatus.UNAUTHORIZED)

def get_username() -> str:
    """
    获取当前登录用户的账户

    Raises:
        UtilException: 获取用户账户异常

    Returns:
        str: 当前登录用户的账户 
    """
    try:
        return get_login_user().user_name
    except Exception as e:
        raise UtilException("获取用户账户异常", HttpStatus.UNAUTHORIZED)

def get_login_user() -> LoginUser:
    """
    获取当前登录用户的信息

    Raises:
        UtilException: 获取用户信息异常

    Returns:
        LoginUser: 当前登录用户的信息 
    """
    try:
        if not current_user.is_authenticated:
            abort(401)
        return current_user
    except Exception:
        raise UtilException("获取用户信息异常", HttpStatus.UNAUTHORIZED)

def validate_password_strength(password: str, min_length: int = 8) -> tuple[bool, str]:
    """
    校验密码强度：至少 min_length 位，且同时包含字母和数字。
    Returns:
        (True, "") 通过；(False, "错误说明") 不通过
    """
    if not password or len(password) < min_length:
        return False, f"密码长度至少 {min_length} 位"
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not has_letter or not has_digit:
        return False, "密码须同时包含字母和数字"
    return True, ""

def encrypt_password(password:str) -> str:
    """
    加密密码

    Args:
        password (str): 原始密码

    Returns:
        str: 加密后的密码
    """
    salt = bcrypt.gensalt(rounds=10, prefix=b'2a')
    bcrypt_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return bcrypt_password.decode('utf-8')

def matches_password(raw_password: str, encoded_password) -> bool:
    """
    验证密码是否匹配

    Args:
        raw_password: 原始密码
        encoded_password: 加密后的密码（bcrypt 格式），若为 None 或格式无效则返回 False

    Returns:
        bool: 密码是否匹配
    """
    if not encoded_password:
        return False
    try:
        enc = encoded_password if isinstance(encoded_password, bytes) else encoded_password.encode('utf-8')
        return bcrypt.checkpw(raw_password.encode('utf-8'), enc)
    except (ValueError, TypeError):
        return False

def is_admin(user_id) -> bool:
    """
    判断用户是否为管理员

    Args:
        user_id (int): 用户ID

    Returns:
        bool: 用户是否为管理员
    """
    return user_id is not None and user_id == 1

def login_user_is_admin() -> bool:
    """
    判断当前登录用户是否为管理员

    Returns:
        bool: 当前登录用户是否为管理员
    """
    return is_admin(get_user_id())
