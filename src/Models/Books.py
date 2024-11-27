from pydantic import BaseModel,Field
from typing import Any
from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_mongo import PydanticObjectId
from bson import ObjectId


class Book(BaseModel):
    title : str = None
    author: str = None
    genre:str = None
    book_id: PydanticObjectId = None

class CollectionOfBook(BaseModel):
    books : list[Book]