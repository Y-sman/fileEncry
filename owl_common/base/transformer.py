# -*- coding: utf-8 -*-
# @Author  : balabala

from types import NoneType
from typing import Callable, List, Optional
from datetime import datetime
from typing_extensions import Annotated
from pydantic import BeforeValidator, ValidationInfo

from owl_common.utils.base import DateUtil


def ids_to_list(value: str | int | None) -> Optional[List[int]]:
    """
    验证ids转换为整型列表（如路径参数 "5"、"5,2,3" 或整数 5）

    Args:
        value (str | int | None): 传入参数

    Returns:
        Optional[List[int]]: 整型列表，空或无效时返回空列表
    """
    if value is None:
        return []
    if isinstance(value, int):
        return [value] if value > 0 else []
    s = str(value).strip()
    if not s:
        return []
    return [int(i) for i in s.split(",") if str(i).strip()]


def to_datetime(format=DateUtil.YYYY_MM_DD_HH_MM_SS) \
        -> Callable[[str|NoneType, ValidationInfo], datetime|NoneType]:
    """
    根据指定格式，验证datetime

    Args:
        format (str): 日期格式. Defaults to '%Y-%m-%d %H:%M:%S'.
    """
    def validate_datetime(value:str|NoneType, info:ValidationInfo) \
            -> datetime|NoneType:
        """
        验证datetime

        Args:
            value (str | NoneType): 传入参数
            info (ValidationInfo): pydantic的验证信息

        Raises:
            ValueError: 日期格式错误

        Returns:
            _type_: datetime
        """
        if value:
            if isinstance(value, str):
                # 先尝试使用指定的格式
                try:
                    return datetime.strptime(value, format)
                except ValueError:
                    # 如果失败，尝试其他常见格式
                    formats_to_try = [
                        DateUtil.YYYY_MM_DD_HH_MM_SS,  # '%Y-%m-%d %H:%M:%S'
                        "%a, %d %b %Y %H:%M:%S GMT",  # HTTP GMT 格式
                        "%Y-%m-%dT%H:%M:%S",  # ISO 格式（无时区）
                        "%Y-%m-%dT%H:%M:%S.%f",  # ISO 格式（带微秒）
                        "%Y-%m-%d %H:%M:%S.%f",  # 标准格式（带微秒）
                        DateUtil.YYYY_MM_DD,  # '%Y-%m-%d'
                    ]
                    for fmt in formats_to_try:
                        if fmt == format:  # 已经尝试过了
                            continue
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                    # 所有格式都失败，抛出异常
                    raise ValueError(f"时间数据 '{value}' 无法匹配任何已知格式")
            elif isinstance(value, datetime):
                return value
            raise ValueError(f"Invalid datetime format: {value}")
        else:
            return None
    return validate_datetime


def str_to_int(value: str | int | float | NoneType, info: ValidationInfo) -> int | None:
    """
    验证并转换为整数；空、undefined、null、空串等视为空，返回 None。
    支持 DB 返回的 float（如 101.0）转为 int，避免 Optional[int] 校验报错。

    Args:
        value: 传入参数（str | int | float | None）
        info: pydantic 的验证信息

    Returns:
        int | None: 整数或 None
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value != value or value == float("inf") or value == float("-inf"):
            return None
        return int(value) if value == int(value) else None
    if isinstance(value, str):
        s = value.strip()
        if not s or s.lower() in ("undefined", "null"):
            return None
        if s.isdecimal():
            return int(s)
        raise ValueError(f"Invalid str format, cannot convert to int: {value}")
    # DB 可能返回 Decimal 等可转整型的类型，统一尝试转为 int
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def optional_int(value: str | int | float | NoneType, info: ValidationInfo) -> int | None:
    """
    将任意值转为 int 或 None，用于可选整型字段（如 dept_id）。
    不抛错：无法转换时一律返回 None，保证非必填字段不触发 ValidationError。
    """
    try:
        return str_to_int(value, info)
    except (ValueError, TypeError):
        return None


def int_to_str(value:int|NoneType)-> str:
    if isinstance(value, int):
        return str(value)
    else:
        return value


ids_convertor = Annotated[List[int],BeforeValidator(ids_to_list)]