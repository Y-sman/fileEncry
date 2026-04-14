# -*- coding: utf-8 -*-
# @Author  : balabala

from typing_extensions import Annotated
from pydantic import BeforeValidator, Field, SecretStr

from owl_common.base.transformer import str_to_int
from owl_common.base.model import VoModel


class LoginBody(VoModel):
    
    username: Annotated[str, Field(..., example='admin')]
    
    password: Annotated[SecretStr, Field(..., example='admin')]
    
    code: Annotated[str, Field(default=None, example='1213')]
    
    uuid: Annotated[str, Field(default=None, example='1234567890')]
    
    
class RegisterBody(LoginBody):
    """注册：用户名、邮箱、密码；系统校验密码强度及用户名、邮箱唯一"""
    email: Annotated[str, Field(default=None, example='user@example.com')]


class ResetPwdBody(VoModel):
    """重置密码请求体，确保 password 被正确接收"""
    userId: Annotated[int, Field(..., gt=0, description="用户ID")]
    password: Annotated[str, Field(..., min_length=5, max_length=20, description="新密码")]


class AndroidLoginRequest(VoModel):
    """Android登录请求"""
    
    username: Annotated[str, Field(..., example='admin')]
    
    password: Annotated[str, Field(..., example='admin123')]
    
    deviceId: Annotated[str, Field(default=None, example='device123')]
    
    deviceModel: Annotated[str, Field(default=None, example='Xiaomi MI 10')]


class AndroidRegisterRequest(VoModel):
    """Android注册请求"""
    
    username: Annotated[str, Field(..., example='admin')]
    
    password: Annotated[str, Field(..., example='admin123')]
    
    realName: Annotated[str, Field(..., example='张三')]
    
    phone: Annotated[str, Field(..., example='13800138000')]
    
    deviceId: Annotated[str, Field(default=None, example='device123')]
    
    deviceModel: Annotated[str, Field(default=None, example='Xiaomi MI 10')]
