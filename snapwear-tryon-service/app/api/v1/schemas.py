from pydantic import BaseModel

class TryOnResponse(BaseModel):
    detail: str
