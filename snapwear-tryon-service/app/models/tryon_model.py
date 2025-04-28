from pydantic import BaseModel

class TryOnRequest(BaseModel):
    clothing_item: str
