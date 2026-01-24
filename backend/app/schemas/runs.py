from pydantic import BaseModel

class RunOut(BaseModel):
    id: int
    name: str
    description: str
