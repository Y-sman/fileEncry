# -*- coding: utf-8 -*-
# @Author  : balabala

import dataclasses
from datetime import date
import decimal
import uuid
import typing as t
from flask import Response
from flask.json.provider import DefaultJSONProvider
from werkzeug.exceptions import HTTPException, default_exceptions
from werkzeug.http import http_date

from owl_common.base.model import AjaxResponse

WSGIEnvironment: t.TypeAlias = dict[str, t.Any]


def _update_exceptions():
    """
    更新异常
    """
    for code in default_exceptions.keys():
        exc = default_exceptions[code]
        if isinstance(exc, HTTPException):
            new_exc = HttpException.from_http_exception(exc)
            default_exceptions[code] = new_exc
        else:
            continue


_update_exceptions()
del _update_exceptions


class HttpException(HTTPException):

    code: int | None = None
    description: str | None = None

    def __init__(
        self,
        description: str | None = None,
        response: Response | None = None,
    ) -> None:
        super().__init__()
        if description is not None:
            self.description = description
        self.response = response

    @classmethod
    def from_http_exception(cls, exc: HTTPException) -> "HttpException": 
        """
        从HTTPException转换为HttpException

        Args:
            exc (HTTPException): werkezeug的HTTPException

        Returns:
            HttpException: HttpException
        """
        # 获取描述信息
        # werkzeug 的 HTTPException 在 __init__ 中会设置 self.description
        # 但如果传入 None，可能会使用类属性，所以需要检查
        description = getattr(exc, 'description', None)
        
        # 如果 description 是类属性的默认值，尝试从实例获取实际值
        # 通过检查是否是类属性来判断
        if hasattr(exc.__class__, 'description') and description == exc.__class__.description:
            # 尝试通过 __dict__ 获取实例属性
            if hasattr(exc, '__dict__') and 'description' in exc.__dict__:
                description = exc.__dict__['description']
        
        # 如果仍然为空或等于类默认值，尝试使用 get_description 方法
        if not description or (hasattr(exc.__class__, 'description') and description == exc.__class__.description):
            if hasattr(exc, 'get_description'):
                try:
                    desc = exc.get_description()
                    if desc and desc != exc.__class__.description:
                        description = desc
                except:
                    pass
        
        # 如果仍然为空，使用默认值
        if not description:
            description = "操作失败"
        
        error = cls(description=description, response=exc.response)
        error.code = exc.code
        return error
    
    @property
    def name(self) -> str:
        """
        状态名称
        
        Returns:
            str: 状态名称
        """
        from werkzeug.http import HTTP_STATUS_CODES

        return HTTP_STATUS_CODES.get(self.code, "Unknown Error")  # type: ignore

    def get_description(
        self,
        environ: WSGIEnvironment | None = None,
        scope: dict[str, t.Any] | None = None,
    ) -> str:
        """
        异常描述
        
        Args:
            environ (WSGIEnvironment, optional): 环境变量. Defaults to None.
            scope (dict[str, t.Any], optional): 作用域. Defaults to None.

        Returns:
            str: 异常描述
        """
        return self.description or ""

    def get_body(
        self,
        environ: WSGIEnvironment | None = None,
        scope: dict[str, t.Any] | None = None,
    ) -> str:
        """
        异常响应体
        
        Args:
            environ (WSGIEnvironment, optional): 环境变量. Defaults to None.
            scope (dict[str, t.Any], optional): 作用域. Defaults to None.

        Returns:
            str: 异常响应体
        """
        # 使用 get_description() 方法获取描述，确保不为空
        description = self.get_description(environ, scope)
        if not description:
            # 如果描述为空，使用默认错误消息
            description = "操作失败"
        
        ajax_resposne = AjaxResponse.from_error(msg=description)
        ajax_resposne.code = self.code
        return ajax_resposne.model_dump_json(
            exclude_unset = True,
            exclude_none = True,
        )

    def get_headers(
        self,
        environ: WSGIEnvironment | None = None,
        scope: dict[str, t.Any] | None = None,
    ) -> list[tuple[str, str]]:
        """
        异常请求头
        
        Args:
            environ (WSGIEnvironment, optional): 环境变量. Defaults to None.
            scope (dict[str, t.Any], optional): 作用域. Defaults to None.

        Returns:
            list[tuple[str, str]]: 异常请求头
        """
        return [("Content-Type", "application/json")]


def json_default(obj):
    """
    转化成可序列化对象

    Args:
        obj : 待序列化对象

    Returns:
        _type_: 可序列化对象
    """
    if isinstance(obj, date):
        return http_date(obj) 

    if isinstance(obj, decimal.Decimal):
        return str(obj)
    
    if isinstance(obj, uuid.UUID):
        return obj.hex

    if dataclasses and dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)

    if isinstance(obj, AjaxResponse):
        return obj.model_dump_json()

    if hasattr(obj, "__html__"):
        return str(obj.__html__())

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


class JsonProvider(DefaultJSONProvider):
    """
    自定义json序列化

    Args:
        DefaultJSONProvider: 默认flask的json序列化
    """
    
    default = staticmethod(json_default)


def handle_http_exception(error:HTTPException) -> Response:
    """
    处理http异常

    Args:
        error (HttpException): http异常

    Returns:
        ResponseReturnValue: 响应体
    """
    if not isinstance(error, HttpException):
        error = HttpException.from_http_exception(error)
    return error.get_response()

