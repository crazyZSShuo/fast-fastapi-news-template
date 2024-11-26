from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

DataT = TypeVar('DataT')

class ResponseSchema(BaseModel, Generic[DataT]):
    code: int = 200
    message: str = "Success"
    data: Optional[DataT] = None
