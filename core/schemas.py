from pydantic import BaseModel
from typing import Any, List


class Resposta(BaseModel):
    erro: Any | None = None
    success: Any | None = None