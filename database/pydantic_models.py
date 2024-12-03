from pydantic import BaseModel
from typing import Any, Dict


class QueryModel(BaseModel):
    query: str  # SQL-запрос
    args: Dict[str, Any] | None  # Параметры для SQL-запроса


class PostgresRequest(BaseModel):
    query: str