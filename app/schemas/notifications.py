from pydantic import BaseModel

class CreateNotification(BaseModel):
    target_price: int
    ticker: str

    class Config:
        from_attributes = True