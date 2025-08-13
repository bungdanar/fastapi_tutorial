from enum import Enum
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = Field(
        default=None, description="The description of the item", max_length=300, examples=["A very nice Item"]
    )
    price: float = Field(
        gt=0, description="The price must be greater than 0", examples=[12.34]
    )
    tax: float | None = Field(default=None, examples=[3.45])
    # tags: set[str] = set()
    # images: list[Image]


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


class User(BaseModel):
    username: str
    full_name: str | None = Field(alias='fullName', default=None)


class FilterParams(BaseModel):
    model_config = {
        "extra": 'forbid'
    }

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal['created_at', 'updated_at'] = 'created_at'
    tags: list[str] = []


class Cookies(BaseModel):
    session_id: str | None = None
    facebook_tracker: str | None = None
    google_tracker: str | None = None


class CommonHeaders(BaseModel):
    user_agent: str | None = None
    x_token: list[str] = []


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type: str = "car"


class PlaneItem(BaseItem):
    type: str = "plane"
    size: int
