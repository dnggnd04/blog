from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Optional, TypeVar, Generic

T = TypeVar("T")

class ResponseSchemaBase(BaseModel):
    __abstract__ = True

    code : str = ''
    message : str = ''
    
    def custom_response(self, code: str, message: str):
        self.code = code
        self.message = message
        return self
    
    def success_response(self):
        self.code = '000'
        self.message = 'Success'
        return self
    
class DataResponse(ResponseSchemaBase, GenericModel, Generic[T]):
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True

    def custom_response(self, code: str, message: str, data: T):
        self.code = code
        self.message = message
        self.data = data
        return self
    
    def success_response(self, data: T):
        self.code = '000'
        self.message = 'Success'
        self.data = data
        return self
    
class MetadataSchema(BaseModel):
    current_page: int
    page_size: int
    total_items: int