#!/usr/bin/env python
# -- coding: utf-8 --
# @Time : 2024/09/18

import os.path
from importlib import import_module
from pathlib import Path
import sys
from types import ModuleType
from flask import Blueprint, Flask

from ..base.signal import module_initailize
from .config import CONFIG_CACHE


def path_to_module(file_path:str, root_path:str) -> str:
    """
    文件路径转为模块名称
    
    Args:
        file_path (str): 文件路径
        root_path (str): 根路径
    
    Returns:
        str: 模块名称
    """
    file_path = Path(file_path)
    root_path = Path(root_path).resolve()
    file_relative = file_path.relative_to(root_path)
    module_path = str(file_relative.with_suffix('')).replace(os.sep, '.').replace('\\', '.')
    return module_path


class OwlModuleRegistry(object):
    
    module_prefix = "owl_"
    controller_name = "controller"
    exclude_modules = ["owl_ui"]
    
    def __init__(self, app:Flask=None, proot:str=None):
        self.app = app
        self.proot = proot
        url_prefix = CONFIG_CACHE.get("owl.api.version", "/api")
        if not url_prefix.startswith("/"):
            raise ValueError("url_prefix must start with /")
        self.api = Blueprint(
            "api", 
            __name__, 
            url_prefix=url_prefix
        )
    
    def register_modules(self):
        '''
        注册所有模块
        '''
        self.import_modules()
        self.register_controllers()
    
    def import_modules(self):
        '''
        导入所有模块
        '''
        for modname in os.listdir(self.proot):
            if not modname.startswith(self.module_prefix):
                continue
            if modname in self.exclude_modules:
                continue
            if not os.path.exists(
                os.path.join(self.proot,modname,"__init__.py")
            ):
                self.app.logger.warning(f"模块路径不存在__init__.py文件: {modname}")
                continue
            self.import_module(modname)
        
    def import_module(self, modname:str):
        '''
        导入模块
        
        Args:
            modname (str): 模块名称
        '''
        modpath = os.path.join(self.proot,modname)
        mod = import_module(path_to_module(modpath,self.proot))
        # 发送模块初始化信号，这会触发各个模块的 import_hook 函数设置 reg
        module_initailize.send(mod,registry=self)
        # 确保信号处理完成后再继续
        self.app.logger.debug(f"模块 {modname} 初始化完成，reg 已设置")
    
    def is_registered_module(self, modname:str) -> bool:
        '''
        检查模块是否已经注册
        
        Args:
            modname (str): 模块名称
        Returns:
            bool: 是否已经注册
        '''
        flag = modname in sys.modules
        return flag
        
    def unregister_module(self, mod:ModuleType):
        '''
        注销模块
        
        Args:
            mod (ModuleType): 模块对象
        '''
        if mod in self.default_modules:
            return
        # todo

    def register_controllers(self):
        '''
        注册所有控制层路由
        '''
        print("=" * 60)
        print("开始注册控制器路由...")
        self.app.logger.info("开始注册控制器路由...")
        module_list = [modname for modname in os.listdir(self.proot)
                      if modname.startswith(self.module_prefix) 
                      and modname not in self.exclude_modules
                      and os.path.exists(os.path.join(self.proot, modname, "__init__.py"))]
        print(f"发现模块: {module_list}")
        self.app.logger.info(f"发现模块: {module_list}")
        
        for modname in module_list:
                    if not self.is_registered_module(modname):
                        print(f"[WARN] 模块 {modname} 未被注册，跳过控制器注册")
                        self.app.logger.warning(f"模块 {modname} 未被注册，跳过控制器注册")
                        continue
                    print(f"正在注册模块 {modname} 的控制器...")
                    self.app.logger.info(f"正在注册模块 {modname} 的控制器...")
                    self.register_controller(modname)
        
        # 在注册到 Flask app 之前，检查 Blueprint 中是否有延迟注册的函数
        # 注意：Flask Blueprint 使用延迟注册机制，视图函数只有在注册到 Flask app 后才会出现在 view_functions 中
        try:
            # 检查 Blueprint 的 deferred_functions（延迟注册的函数列表）
            deferred_count = len(self.api.deferred_functions) if hasattr(self.api, 'deferred_functions') else 0
            print(f"Blueprint 中有 {deferred_count} 个延迟注册的函数")
            self.app.logger.info(f"Blueprint 中有 {deferred_count} 个延迟注册的函数")
            
            # 列出延迟注册的函数名称（用于调试）
            if hasattr(self.api, 'deferred_functions') and deferred_count > 0:
                deferred_funcs = []
                for func in self.api.deferred_functions:
                    if hasattr(func, '__name__'):
                        deferred_funcs.append(func.__name__)
                    elif callable(func):
                        deferred_funcs.append(str(func))
        except Exception as e:
            self.app.logger.error(f"检查 Blueprint 延迟注册函数时出错: {str(e)}", exc_info=True)
        
        # 注册 Blueprint 到 Flask app（此时延迟注册的函数才会真正注册）
        self.app.register_blueprint(self.api)
        print(f"[OK] API Blueprint 已注册到 Flask app，URL前缀: {self.api.url_prefix}")
        self.app.logger.info(f"API Blueprint 已注册到 Flask app，URL前缀: {self.api.url_prefix}")
        
        # 记录已注册的路由（从 Flask app 的 url_map 中查找该 Blueprint 的路由）
        registered_routes = [str(rule) for rule in self.app.url_map.iter_rules() 
                            if hasattr(rule, 'endpoint') and rule.endpoint.startswith('api.')]
        self.app.logger.info(f"API Blueprint 共注册了 {len(registered_routes)} 个路由")
        
        self.app.logger.debug(f"已注册的API路由列表（前20个）: {registered_routes[:20]}")  # 只显示前20个
    
    def register_controller(self, modname:str):
        '''
        注册控制层路由
        
        Args:
            mod (str): 模块名称
        '''
        modpath = os.path.join(self.proot,modname)
        mod_con_path = os.path.join(modpath,self.controller_name)
        if not os.path.exists(mod_con_path):
            return  
        try:
            self._register_rules(mod_con_path)
            self.app.logger.info(f"✓ 成功注册模块 {modname} 的控制器路由")
            print(f"[OK] 成功注册模块 {modname} 的控制器路由")
        except Exception as e:
            self.app.logger.error(f"✗ 在模块中的路由，注册失败: {modname}，原因: {str(e)}", exc_info=True)
            raise Exception(
                "在模块中的路由，注册失败: {}，原因: {}".format(modname,str(e))
            )
    
    def unregister_controller(self, modname:str):
        '''
        注销控制层路由
        
        Args:
            modname (str): 模块名称
        '''
        # todo
    
    
    def _register_rules(self,path:str):
        '''
        注册路由规则
        
        Args:
            path (str): 路由路径
        '''
        for rule_name in sorted(os.listdir(path)):  # 排序以确保导入顺序一致
            con_path = os.path.join(path,rule_name)
            if os.path.isfile(con_path) and rule_name.endswith(".py") \
                and rule_name != "__init__.py":
                rule_path = path_to_module(con_path,self.proot)
                try:
                    # 提取模块名称（例如：owl_security.controller.security_android_auth -> owl_security）
                    modname = rule_path.split('.')[0]
                    # 确保模块已注册，reg 已设置
                    if modname in sys.modules:
                        mod = sys.modules[modname]
                        # 检查 reg 是否已设置，如果没有则重新发送信号
                        try:
                            if not hasattr(mod, 'reg') or mod.reg is None:
                                self.app.logger.warning(f"模块 {modname} 的 reg 未设置，重新发送初始化信号")
                                module_initailize.send(mod, registry=self)
                        except (AttributeError, NameError):
                            self.app.logger.warning(f"模块 {modname} 的 reg 未定义，重新发送初始化信号")
                            module_initailize.send(mod, registry=self)
                    
                    # 导入控制器文件
                    print(f"  → 正在导入控制器文件: {rule_path}")
                    self.app.logger.info(f"正在导入控制器文件: {rule_path}")
                    
                    # 记录导入前的 Blueprint 状态
                    try:
                        if hasattr(self.api, 'deferred_functions'):
                            deferred_before = len(self.api.deferred_functions)
                        else:
                            deferred_before = 0
                        if hasattr(self.api, 'view_functions'):
                            views_before = len(self.api.view_functions)
                        else:
                            views_before = 0
                    except:
                        deferred_before = 0
                        views_before = 0
                    
                    import_module(rule_path)
                    
                    # 记录导入后的 Blueprint 状态
                    try:
                        if hasattr(self.api, 'deferred_functions'):
                            deferred_after = len(self.api.deferred_functions)
                        else:
                            deferred_after = 0
                        if hasattr(self.api, 'view_functions'):
                            views_after = len(self.api.view_functions)
                        else:
                            views_after = 0
                        deferred_added = deferred_after - deferred_before
                        views_added = views_after - views_before
                        print(f"  [OK] 成功导入控制器文件: {rule_path}")
                        print(f"     新增延迟函数: {deferred_added}, 新增视图函数: {views_added}")
                        if views_added > 0:
                            new_views = [k for k in list(self.api.view_functions.keys())[-views_added:]]
                            print(f"     新增视图: {new_views}")
                    except Exception as e:
                        print(f"  [WARN] 无法检查导入后的状态 {rule_path}: {str(e)}")
                        self.app.logger.warning(f"无法检查导入后的状态 {rule_path}: {str(e)}")
                    
                    # 验证路由是否已注册（通过检查 Blueprint 的装饰器）
                    # 注意：此时路由还没有注册到 Flask app，所以检查 Blueprint 本身的路由
                    try:
                        imported_module = sys.modules[rule_path]
                        routes_in_file = [name for name in dir(imported_module) 
                                         if not name.startswith('_') and callable(getattr(imported_module, name, None))]
                        self.app.logger.info(f"✓ 成功导入控制器文件: {rule_path}，定义了函数: {routes_in_file[:5]}")
                    except Exception as e:
                        self.app.logger.warning(f"无法检查导入的模块 {rule_path}: {str(e)}")
                except Exception as e:
                    self.app.logger.error(f"导入控制器文件失败: {rule_path}，原因: {str(e)}", exc_info=True)
                    raise
            elif os.path.isdir(con_path) and \
                os.path.exists(os.path.join(con_path,"__init__.py")):
                for sub_rule_name in sorted(os.listdir(con_path)):
                    sub_path = os.path.join(con_path,sub_rule_name)
                    if os.path.isfile(sub_path) and sub_rule_name.endswith(".py") \
                        and sub_rule_name != "__init__.py":
                        rule_path = path_to_module(sub_path,self.proot)
                        try:
                            # 提取模块名称
                            modname = rule_path.split('.')[0]
                            # 确保模块已注册，reg 已设置
                            if modname in sys.modules:
                                mod = sys.modules[modname]
                                try:
                                    if not hasattr(mod, 'reg') or mod.reg is None:
                                        self.app.logger.warning(f"模块 {modname} 的 reg 未设置，重新发送初始化信号")
                                        module_initailize.send(mod, registry=self)
                                except (AttributeError, NameError):
                                    self.app.logger.warning(f"模块 {modname} 的 reg 未定义，重新发送初始化信号")
                                    module_initailize.send(mod, registry=self)
                            
                            # 导入控制器文件
                            self.app.logger.info(f"正在导入控制器文件: {rule_path}")
                            import_module(rule_path)
                            self.app.logger.info(f"✓ 成功导入控制器文件: {rule_path}")
                        except Exception as e:
                            self.app.logger.error(f"导入控制器文件失败: {rule_path}，原因: {str(e)}", exc_info=True)
                            raise
            else:
                continue
