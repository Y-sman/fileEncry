
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict
from flask import g, request
from pydantic import BaseModel, ValidationError
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from werkzeug.exceptions import BadRequest,UnsupportedMediaType

from owl_common.base.model import BaseEntity, CriterianMeta, ExtraModel, \
    BaseEntity, OrderModel, PageModel, VoValidatorContext
from owl_common.base.schema_vo import BaseSchemaFactory, QuerySchemaFactory


class AbsReqParser(ABC):
    
    @abstractmethod
    def data(self) -> Dict:
        """
        获取请求参数

        Returns:
            Dict: 请求参数字典
        """
    
    @abstractmethod
    def cast_model(self, bo_model:BaseEntity) -> BaseModel:
        """
        适配模型

        Args:
            bo_model (BaseEntity): Vo模型
            src_model (BaseModel): 源模型

        Returns:
            BaseModel: 适配后的模型
        """
    
    @abstractmethod
    def prepare_factory(self, factory:BaseSchemaFactory):
        """
        准备工厂

        Args:
            factory (BaseSchemaFactory): 工厂
        """
    
    @abstractmethod
    def prepare(self):
        """
        准备数据
        """ 

class BaseReqParser(AbsReqParser):
    
    def data(self) -> Dict:
        pass
    
    def cast_model(self, bo_model:BaseEntity) -> BaseModel:
        pass
    
    def prepare_factory(self, factory:BaseSchemaFactory):
        pass

    def prepare(self):
        pass
    

class QueryReqParser(BaseReqParser):

    def __init__(self, context:VoValidatorContext):
        self.context = context
        self.extra_model = ExtraModel
    
    def prepare_factory(self, factory: QuerySchemaFactory):
        if factory.extra_model:
            self.extra_model = factory.extra_model
            
    def prepare(self):
        self.criterian_meta = CriterianMeta()
        g.criterian_meta = self.criterian_meta
    
    def validate_request(self) -> Dict:
        return request.args.to_dict()
    
    def data(self) -> Dict:
        data = self.validate_request().copy()
        try:
            if self.context.is_page:
                page = PageModel.model_validate(data,context=self.context)
                # 始终设置 page，确保分页生效（即使请求未显式传分页参数也使用默认值）
                self.criterian_meta.page = page
            if self.context.is_sort:
                sort = OrderModel.model_validate(data,context=self.context)
                if sort.model_fields_set:
                    self.criterian_meta.sort = sort
            if self.extra_model:
                extra = self.extra_model.model_validate(data,context=self.context)
                if extra.model_fields_set:
                    self.criterian_meta.extra = extra
        except ValidationError as e:
            # 如果是分页或排序验证失败，应该抛出异常，让上层处理
            import logging
            error_messages = []
            if hasattr(e, 'errors'):
                for error in e.errors():
                    field = error.get('loc', ('unknown',))[-1]
                    msg = error.get('msg', 'Validation error')
                    error_messages.append(f"{field}: {msg}")
            error_desc = "; ".join(error_messages) if error_messages else str(e)
            logging.error(f"Page/Sort/Extra model validation failed: {error_desc}")
            # 重新抛出ValidationError，让上层捕获处理
            raise
        except Exception as e:
            # 其他异常，记录详细错误信息但不中断
            import logging
            logging.warning(f"Extra model validation failed: {e}")
        return data
    
    def cast_model(self, bo_model:BaseEntity) -> BaseModel:
        data = self.data().copy()
        # 移除分页和排序参数，这些参数不应该参与实体模型的验证
        data.pop('pageNum', None)
        data.pop('pageSize', None)
        data.pop('page_num', None)
        data.pop('page_size', None)
        data.pop('orderByColumn', None)
        data.pop('order_by_column', None)
        data.pop('isAsc', None)
        data.pop('is_asc', None)
        bo = bo_model.model_validate(data)
        return bo
    
    
@dataclass
class PathReqParser(BaseReqParser):
    
    def data(self) -> Dict:
        return request.view_args.copy()
        

@dataclass
class BodyReqParser(BaseReqParser):
    
    minetype: ClassVar[str] = "application/json"

    def __init__(self, context:VoValidatorContext):
        self.context = context
        
    def validate_request(self) -> Dict:
        content_type = request.headers.get("Content-Type", "").lower()
        minetype = content_type.split(";")[0]
        if minetype == self.minetype:
            body: dict | list = request.get_json()
            if not body:
                raise BadRequest(
                    description="在{}, body数据不能为空".format(content_type),
                )
        else:
            raise UnsupportedMediaType(
                description="content-type仅支持application/json"
            )
        return body
    
    def data(self) -> Dict:
        data = self.validate_request().copy()
        return data

    def cast_model(self, bo_model:BaseEntity) -> BaseModel:
        data = self.data()
        # 过滤掉不在模型字段中的额外字段，避免 extra="forbid" 错误
        if isinstance(data, dict) and hasattr(bo_model, 'model_fields'):
            # 收集所有有效的字段名和别名
            valid_keys = set()
            for k, finfo in bo_model.model_fields.items():
                valid_keys.add(k)
                # 获取验证别名
                if hasattr(bo_model, 'get_validation_alias'):
                    try:
                        alias_set = bo_model.get_validation_alias(k, finfo)
                        if alias_set and isinstance(alias_set, (set, list, tuple)):
                            valid_keys.update(alias_set)
                    except:
                        pass
                # 也检查字段的 validation_alias
                if hasattr(finfo, 'validation_alias'):
                    if isinstance(finfo.validation_alias, str):
                        valid_keys.add(finfo.validation_alias)
                    elif hasattr(finfo.validation_alias, '__iter__') and not isinstance(finfo.validation_alias, str):
                        try:
                            valid_keys.update(finfo.validation_alias)
                        except:
                            pass
            # 只保留有效字段，移除所有不在模型中的字段（包括 create_time 等）
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            
            # 临时修改模型配置，允许忽略额外字段
            original_config = None
            if hasattr(bo_model, 'model_config'):
                original_config = bo_model.model_config
                # 如果配置是 extra="forbid"，临时改为 extra="ignore"
                if isinstance(original_config, dict) and original_config.get('extra') == 'forbid':
                    from pydantic import ConfigDict
                    temp_config = dict(original_config)
                    temp_config['extra'] = 'ignore'
                    bo_model.model_config = ConfigDict(**temp_config)
            
            try:
                bo = bo_model.model_validate(filtered_data, context=self.context)
            finally:
                # 恢复原始配置
                if original_config is not None:
                    bo_model.model_config = original_config
        else:
            bo = bo_model.model_validate(data, context=self.context)
        return bo


@dataclass
class FormUrlencodedQueryReqParser(QueryReqParser):
    
    minetype: ClassVar[str] = "application/x-www-form-urlencoded"
    
    def __init__(self, context:VoValidatorContext):
        super().__init__(context)
    
    def validate_request(self) -> Dict:
        content_type = request.headers.get("Content-Type", "").lower()
        minetype = content_type.split(";")[0]
        if minetype == self.minetype:
            form:ImmutableMultiDict = request.form
            body = form.to_dict()
        else:
            raise UnsupportedMediaType(
                description="除了{},content-type不支持{}".format(self.minetype,minetype)
            )
        return body


@dataclass
class DownloadFileQueryReqParser(FormUrlencodedQueryReqParser):
    
    def __init__(self, context:VoValidatorContext):
        super().__init__(context)


class FormReqParser(BaseReqParser):
    
    minetype: ClassVar[str] = "multipart/form-data"
    
    def __init__(
        self, 
        is_form:bool=True,
        is_query:bool=False,
        is_file:bool|None=None,
        ):
        self.is_form = is_form
        self.is_query = is_query
        self.is_file = is_file
        
    def validate_request(self) -> Dict:
        content_type = request.headers.get("Content-Type", "").lower()
        minetype = content_type.split(";")[0]
        new_data = {}
        if minetype == self.minetype or (not self.is_file and not content_type):
            # 如果是 multipart/form-data 或者没有 Content-Type（某些客户端可能不发送）
            if self.is_form:
                new_data.update(request.form.to_dict())
            if self.is_query:
                new_data.update(request.args.to_dict())
            if self.is_file:
                files_dict = request.files.to_dict(flat=False)
                if not files_dict:
                    raise BadRequest(description="未找到上传的文件，请确保使用 multipart/form-data 格式上传")
                new_data.update(files_dict)
        else:
            raise UnsupportedMediaType(
                description="除了{},content-type不支持{}".format(self.minetype,minetype)
            )
        return new_data
    
    def data(self) -> Dict:
        data = self.validate_request()
        return data

    
class UploadFileFormReqParser(FormReqParser):
    
    def prepare(self):
        """准备数据解析器"""
        pass
    
    def validate_request(self) -> Dict:
        return super().validate_request()

    def data(self) -> Dict:
        from owl_common.base.model import MultiFile
        from werkzeug.datastructures import ImmutableMultiDict
        data = self.validate_request()
        # 将文件字典转换为 MultiFile 对象
        for key, value in list(data.items()):
            if isinstance(value, list) and len(value) > 0:
                # 检查列表中的第一个元素是否是 FileStorage
                if isinstance(value[0], FileStorage):
                    # 如果是文件列表，转换为 MultiFile
                    files_dict = {key: value}
                    files_immutable = ImmutableMultiDict(files_dict)
                    data[key] = MultiFile.from_obj(files_immutable)
            elif isinstance(value, FileStorage):
                # 如果是单个文件，也转换为 MultiFile
                files_dict = {key: [value]}
                files_immutable = ImmutableMultiDict(files_dict)
                data[key] = MultiFile.from_obj(files_immutable)
        return data
    
            
class StreamReqParser(BaseReqParser):

    minetype: ClassVar[str] = "application/octet-stream"

    def data(self, *args, **kwargs) -> Dict:
        pass