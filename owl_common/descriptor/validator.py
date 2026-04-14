
import inspect
from abc import ABC, abstractmethod
from functools import wraps
from dataclasses import dataclass, field
from typing import Annotated, Any, Callable,  Dict, Tuple, Type, ClassVar, \
    Optional, Set
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError, UnsupportedMediaType
from flask import has_request_context
from pydantic import BaseModel, ValidationError, validate_call
from pydantic.fields import FieldInfo

from owl_common.base.reqparser import BaseReqParser, BodyReqParser, \
    DownloadFileQueryReqParser, UploadFileFormReqParser, PathReqParser, \
    QueryReqParser, VoValidatorContext
from owl_common.base.schema_vo import ArbitrarySchemaFactory, \
    BaseSchemaFactory, BodySchemaFactory, PathSchemaFactory, QuerySchemaFactory
from owl_common.base.model import MultiFile


class AbcValidatorFunction(ABC):
    
    @abstractmethod
    def validate_unbound_parameters(self):
        raise NotImplementedError()

    @abstractmethod
    def validate_function(self):
        raise NotImplementedError()
    
    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()
    

class ValidatorScopeFunction(AbcValidatorFunction):
    
    def __init__(self,func:Callable):
        self.func = func
        self.sig = inspect.signature(self.func)
        self._unbound_fields:Dict[str,Annotated] = {}
        self._unbound_model: \
            Optional[Tuple[str,Type[BaseModel],Type[BaseModel]]] = None
        self.args = ()
        self.kwargs = {}
        self.validate_unbound_parameters()
        self.validate_function()

    @property
    def unbound_model(self):
        return self._unbound_model
    
    def _validate_kind(self,kind):
        if kind != inspect.Parameter.POSITIONAL_OR_KEYWORD:
            raise Exception("参数必须是位置参数")
    
    def validate_unbound_parameters(self):
        index = 0
        for key in self.sig.parameters:
            param = self.sig.parameters[key]
            self._validate_kind(param.kind)
            if isinstance(param.annotation, BaseModel):
                self._unbound_model = (key,param.annotation)
                if index > 0:
                    raise Exception(
                        f"{self.func.__name__} 类型参数有且仅有第一个"
                    )
            else:
                self._unbound_fields[key] = \
                    FieldInfo.from_annotation(param.annotation)
            index += 1
        
    def validate_function(self):
        self.func = validate_call(self.func)
            
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.args = args if args else ()
        self.kwargs = kwargs if kwargs else {}
        return self.func(*self.args, **self.kwargs)
    

class ValidatorViewFunction(AbcValidatorFunction):
        
    def __init__(self,func:Callable):
        self.func = func
        self.sig = inspect.signature(self.func)
        self._unbound_fields:Dict[str,Annotated] = {}
        self._unbound_model: \
            Optional[Tuple[str,Type[BaseModel],Type[BaseModel]]] = None
        self._schema_factory = None
        self._data_parser = None
        self.args = ()
        self.kwargs = {}

    @property
    def unbound_model(self):
        return self._unbound_model
    
    def _validate_kind(self,kind):
        if kind != inspect.Parameter.POSITIONAL_OR_KEYWORD:
            raise Exception("参数必须是位置参数")
    
    def validate_unbound_parameters(self):
        index = 0
        for key in self.sig.parameters:
            param = self.sig.parameters[key]
            self._validate_kind(param.kind)
            if self._schema_factory:
                annotation = self._schema_factory. \
                    validate_annotation(param.annotation)
                if annotation:
                    self._unbound_model = (key,annotation)
                    if index > 0:
                        raise Exception(
                            f"{self.func.__name__} 类型参数有且仅有第一个"
                        )
                else:
                    self._unbound_fields[key] = \
                        FieldInfo.from_annotation(param.annotation)
            else:
                if isinstance(param.annotation, BaseModel):
                    self._unbound_model = (key,param.annotation)
                    if index > 0:
                        raise Exception(
                            f"{self.func.__name__} 类型参数有且仅有第一个"
                        )
                else:
                    self._unbound_fields[key] = \
                        FieldInfo.from_annotation(param.annotation)
            index += 1
        
    def validate_function(self):
        # 检查是否有 MultiFile 类型的参数
        has_multifile = False
        multifile_params = []
        for param_name, param in self.sig.parameters.items():
            if param.annotation == MultiFile:
                has_multifile = True
                multifile_params.append(param_name)
        
        # 检查是否只有基本类型参数（PathValidator 的情况）
        is_path_validator = isinstance(self._schema_factory, PathSchemaFactory) if self._schema_factory else False
        has_only_basic_types = True
        if is_path_validator and not self._unbound_model:
            for param_name, param in self.sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    # 检查是否是基本类型（int, str, float, bool 等）
                    annotation = param.annotation
                    # 获取实际的类型（处理 Optional, Annotated 等）
                    if hasattr(annotation, '__origin__'):
                        annotation = annotation.__origin__
                    if hasattr(annotation, '__args__') and len(annotation.__args__) > 0:
                        annotation = annotation.__args__[0]
                    if annotation not in (int, str, float, bool) and annotation != inspect.Parameter.empty:
                        # 如果注解不是基本类型，尝试检查是否是 type 的实例
                        if not isinstance(annotation, type) or annotation in (object, Any):
                            has_only_basic_types = False
                            break
        
        if self._schema_factory:
            config = self._schema_factory.model_config
            # ArbitrarySchemaFactory 已经设置了 arbitrary_types_allowed=True
            # 但是对于 MultiFile 类型，我们需要跳过类型验证
            if has_multifile:
                # 如果有 MultiFile 参数，不进行 validate_call，因为我们会在 bound_data 中手动绑定参数
                # 这样可以避免 validate_call 对 MultiFile 类型的验证问题
                self.func = self.func  # 不进行 validate_call
            elif is_path_validator and has_only_basic_types and not self._unbound_model:
                # 对于 PathValidator 且只有基本类型参数的情况，Flask 已经处理了类型转换
                # 不需要 validate_call，避免验证错误
                self.func = self.func
            elif self._unbound_model:
                self.func = validate_call(
                    self.func,
                    config=config)
            else:
                self.func = validate_call(
                    self.func,
                    config=config
                )
        else:
            if has_multifile:
                # 如果有 MultiFile 参数，不进行 validate_call
                self.func = self.func  # 不进行 validate_call
            else:
                self.func = validate_call(self.func)

    def unbound_data(
        self, 
        data_parser: BaseReqParser
        ):
        self._data_parser = data_parser
        if self._schema_factory and self._data_parser:
            self._data_parser.prepare_factory(self._schema_factory)
    
    def unbound_schema(
        self, 
        schema_factory:Optional[BaseSchemaFactory], 
        ):
        self._schema_factory = schema_factory
        self.validate_unbound_parameters()
        self.validate_function()
    
    def bound_data(self, args:Tuple=(), kwargs:Dict={}):
        if self._unbound_model:
            key, bo_model = self._unbound_model
            # 检查函数参数数量
            if self.sig:
                param_count = len(self.sig.parameters)
                if param_count == 1:
                    # 如果函数只有一个参数（模型参数），清空所有其他参数
                    # 这样可以避免 validate_call 从查询参数中解析同名参数导致的冲突
                    self.args = ()
                    # 只保留模型参数，移除所有其他可能的冲突参数
                    kwargs.clear()
            else:
                # 如果没有签名信息，先移除可能存在的同名参数
                kwargs.pop(key, None)
            obj = self._data_parser.cast_model(bo_model)
            kwargs[key] = obj
        else:
            data = self._data_parser.data()
            # 对于路径参数，不要清空 kwargs，而是更新它
            # 这样可以保留 Flask 传递过来的正确类型的参数
            if data:
                kwargs.update(data)
            # 如果没有 data 且 kwargs 为空，保持原样
            
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.args = args if args else ()
        self.kwargs = kwargs if kwargs else {}
        if not has_request_context:
            raise Exception("请在flask请求上下文中调用")
        try:
            if self._data_parser:
                self._data_parser.prepare()
                self.bound_data(self.args, self.kwargs)
            # 调用函数，validate_call 会自动验证参数（如果有的话）
            return self.func(*self.args, **self.kwargs)
        except ValidationError as e:
            # 格式化 ValidationError 错误信息，使其更易读
            error_messages = []
            if hasattr(e, 'errors'):
                for error in e.errors():
                    field = error.get('loc', ('unknown',))[-1]
                    msg = error.get('msg', 'Validation error')
                    error_messages.append(f"{field}: {msg}")
            error_desc = "; ".join(error_messages) if error_messages else str(e)
            import logging
            logging.error(f"ValidationError in {self.func.__name__}: {error_desc}")
            return BadRequest(description=f"验证失败: {error_desc}")
        except TypeError as e:
            import logging
            logging.error(f"TypeError in {self.func.__name__}: {str(e)}")
            return BadRequest(description=f"类型错误: {str(e)}")
        except BadRequest as e:
            # 直接返回 BadRequest 异常（如 Content-Type 错误）
            import logging
            logging.error(f"BadRequest in {self.func.__name__}: {str(e.description) if hasattr(e, 'description') else str(e)}")
            return e
        except UnsupportedMediaType as e:
            # 将 UnsupportedMediaType 转换为 BadRequest
            error_msg = str(e.description) if hasattr(e, 'description') else str(e)
            import logging
            logging.error(f"UnsupportedMediaType in {self.func.__name__}: {error_msg}")
            return BadRequest(description=error_msg)
        except HTTPException as e:
            # 捕获其他所有 HTTPException（包括 ServiceException 等）
            # 重新抛出，让 Flask 的错误处理器处理
            import logging
            error_msg = str(e.description) if hasattr(e, 'description') and e.description else str(e)
            logging.error(f"HTTPException in {self.func.__name__}: {error_msg}")
            raise e  # 重新抛出，让 Flask 的错误处理器处理
        except Exception as e:
            import traceback
            import logging
            error_trace = traceback.format_exc()
            logging.error(f"Exception in {self.func.__name__}: {str(e)}\n{error_trace}")
            return InternalServerError(description=f"内部错误: {str(e)}\n{error_trace}")


@dataclass
class BaseValidator:
    
    data_parser:ClassVar = None
    
    schema_factory:ClassVar = None
    
    vo_context:VoValidatorContext = field(init=False)
    
    def __call__(self, func):
        
        view_function = ValidatorViewFunction(func)
        view_function.unbound_schema(self.schema_factory)
        view_function.unbound_data(self.data_parser)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return view_function(*args, **kwargs)
        return wrapper
    

@dataclass
class PathValidator(BaseValidator):
    
    def __post_init__(self):
        self.schema_factory = PathSchemaFactory()
        self.data_parser = PathReqParser()


@dataclass
class QueryValidator(BaseValidator):
    
    is_page: bool = False
    
    include:Optional[Set[str]] = field(default=None)
    
    exclude:Optional[Set[str]] = field(default=None)
    
    extra_fields:Optional[Dict[str, FieldInfo]] = field(default=None)
    
    def __post_init__(self):
        vo_context = VoValidatorContext(
            exclude_data_alias=True,
            is_page=self.is_page,
            is_sort=self.is_page,
            include_fields=self.include,
            exclude_fields=self.exclude,
        )
        self.schema_factory = QuerySchemaFactory(
            vo_context,
            extra_strict_forbid=True,
            extra_allowed_fields=self.extra_fields
        )
        self.data_parser = QueryReqParser(vo_context)
        

@dataclass
class BodyValidator(BaseValidator):
    
    include:Optional[Set[str]] = field(default=None)
    exclude:Optional[Set[str]] = field(default=None)
    
    def __post_init__(self):
        vo_context = VoValidatorContext(
            include_fields=self.include,
            exclude_fields=self.exclude
        )
        self.schema_factory = BodySchemaFactory(vo_context)
        self.data_parser = BodyReqParser(vo_context)


@dataclass
class FileDownloadValidator(BaseValidator):
    
    def __post_init__(self):
        vo_context = VoValidatorContext(
            exclude_data_alias=True,
            is_page=True,
        )
        self.schema_factory = QuerySchemaFactory(vo_context)
        self.data_parser = DownloadFileQueryReqParser(vo_context)


@dataclass
class FileUploadValidator(BaseValidator):
        
    def __post_init__(self):
        self.schema_factory = ArbitrarySchemaFactory()
        self.data_parser = UploadFileFormReqParser(
            is_form=False, is_query=True, is_file=True
        )


@dataclass
class FileValidator(BaseValidator):
    
    include:Optional[Set[str]] = field(default=None)
    
    def __post_init__(self):
        self.schema_factory = ArbitrarySchemaFactory()
        self.data_parser = UploadFileFormReqParser(is_form=False, is_query=False, is_file=True)
        
