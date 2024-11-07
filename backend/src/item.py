from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str
    price: float

class Account(BaseModel):
    firstName: str
    lastName: str
    sex: float
    program: float
    email: str
    password: str
