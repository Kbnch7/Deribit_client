from pydantic import BaseModel

class TickerName(BaseModel):
    name: str

    class Config:
        from_attributes = True
