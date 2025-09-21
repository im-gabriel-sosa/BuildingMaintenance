# backend/app/api/utils.py
from bson import ObjectId
from typing import Any


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        # For Pydantic v1 compatibility
        yield cls.validate

    @classmethod
    def validate(cls, v: Any, _: Any = None) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        # For Pydantic v1 compatibility
        field_schema.update(type="string")
        return field_schema

    @classmethod
    def __modify_schema__(cls, field_schema):
        # Alternative method for schema modification
        field_schema.update(type="string")

    def __str__(self):
        return str(super())

    def __repr__(self):
        return f"PyObjectId('{str(self)}')"