from pydantic import BaseModel, conint
from pydantic.generics import GenericModel
from typing import Optional, Generic, TypeVar, Sequence, Type
from abc import ABC, abstractmethod
from contextvars import ContextVar
from sqlalchemy.orm import Query
from sqlalchemy import asc, desc
from fastapi.exceptions import HTTPException
from fastapi import status, Depends

from app.schemas.sche_base import ResponseSchemaBase, MetadataSchema

T = TypeVar("T")
C = TypeVar("C")

class PaginationParams(BaseModel):
    page_size: Optional[conint(gt=0, lt=1001)] = 10
    page: Optional[conint(gt=0)] = 1
    sort_by: Optional[str] = 'id'
    order: Optional[str] = 'desc'

class BasePage(ResponseSchemaBase, GenericModel, Generic[T], ABC):
    data: Sequence[T]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    @abstractmethod
    def create(cls, code: str, message: str, data: Sequence[T], metadata: MetadataSchema) -> C:
        pass

class Page(BasePage[T], Generic[T]):
    metadata: MetadataSchema

    @classmethod
    def create(cls, code: str, message: str, data: Sequence[T], metadata: MetadataSchema) -> C:
        return cls(
            code = code,
            message = message,
            data = data,
            metadata = metadata
        )

PageType: ContextVar[Type[BasePage]] = ContextVar("PageType", default=Page)

def paginate(model, query: Query, params: Optional[PaginationParams]) -> BasePage:
    code = '200'
    message = 'success'

    try:
        total = query.count()

        if params.order:
            direction = desc if params.order == 'desc' else asc
            query = query.order_by(direction(getattr(model, params.sort_by)))
        
        data = query.limit(params.page_size).offset(params.page_size * (params.page - 1)).all()

        metadata = MetadataSchema(
            current_page=params.page,
            page_size=params.page_size,
            total_items=total
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Khong the query"
        )
    
    return PageType.get().create(code, message, data, metadata)