import logging
from functools import cached_property
from typing import (
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
)

import peewee
import pydantic

from app.database.database import objects
from app.database.model.base_model import BaseModel
from app.utils.encoders import jsonable_encoder

Model = TypeVar('Model', bound=BaseModel)
PrimaryKey = Union[int, str, Model]


class CRUDBase(Generic[Model]):
    def __init__(self, model: Type[Model]):
        self.model = model
        self.logger = logging.getLogger(self.__class__.__qualname__)

    @cached_property
    def primary_key(self) -> Optional[peewee.Field]:
        return self.model._meta.primary_key

    @cached_property
    def primary_key_name(self) -> Optional[str]:
        return self.primary_key.safe_name

    async def get(self, primary_key: PrimaryKey) -> Optional[Model]:
        query = self.model.select().where(self.primary_key == primary_key)
        return await objects.first(query)

    async def get_multi(
            self,
            *,
            select: list[Model] = None,
            limit: int = None,
            offset: int = None,
            offset_id: PrimaryKey = None,
            reverse: bool = False,
    ) -> list[Model]:
        query = self.model.select(*(select or []))

        if offset_id is not None:
            if reverse:
                query = query.where(self.primary_key < offset_id).order_by(self.primary_key.desc())
            else:
                query = query.where(self.primary_key > offset_id).order_by(self.primary_key)

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return await objects.execute(query)

    async def create(self, *, create_object: Union[dict, pydantic.BaseModel] = None, **kwargs) -> Model:
        create_data = {**jsonable_encoder(create_object or {}), **jsonable_encoder(kwargs)}
        return await objects.create(self.model, **create_data)

    async def update(
            self,
            db_obj: Model,
            *,
            update_object: Union[dict, pydantic.BaseModel] = None,
            partial: bool = False,
            only: bool = None,
            **kwargs
    ) -> Model:
        update_data = {**jsonable_encoder(update_object or {}, exclude_unset=partial), **jsonable_encoder(kwargs)}
        obj_data_fields = jsonable_encoder(db_obj).get('__data__', [])

        for field in obj_data_fields:
            if field in update_data:
                try:
                    setattr(db_obj, field, update_data[field])
                except (AttributeError, ValueError, KeyError):
                    pass

        await objects.update(db_obj, only=only)
        return db_obj

    async def create_or_update(self, *, data_object: Union[dict, pydantic.BaseModel] = None, **kwargs) -> Model:
        data = {**jsonable_encoder(data_object or {}), **jsonable_encoder(kwargs)}
        obj_id = data.get(self.primary_key_name)

        if bool(obj_id):
            obj = await self.get(obj_id)

            if bool(obj):
                return await self.update(obj, update_object=data)

        return await self.create(create_object=data)

    async def delete(self, obj: Model, *, recursive: bool = False, delete_nullable: bool = False) -> Model:
        await objects.delete(obj, recursive=recursive, delete_nullable=delete_nullable)
        return obj
