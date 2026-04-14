# -*- coding: utf-8 -*-
# @Author  : balabala

import sys
from types import ModuleType

from owl_common.descriptor.listener import ModuleSignalListener
from owl_common.base.signal import module_initailize
from owl_common.owl.registry import OwlModuleRegistry


reg: OwlModuleRegistry


@ModuleSignalListener(sys.modules[__name__], module_initailize)
def import_hook(module: ModuleType, registry: OwlModuleRegistry):
    """
    导入模块时设置注册器
    """
    global reg
    reg = registry


# 导入模型类，确保 SQLAlchemy 注册到 metadata
from .domain import po
