from pydantic import BaseModel


class PriceResponse(BaseModel):
    ticker: str
    price: float
    timestamp: int

    class Config:
        from_attributes = True

class LinearPriceChart(BaseModel):
    time: int
    value: float

    class Config:
        from_attributes = True
