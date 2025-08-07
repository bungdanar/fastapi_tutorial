from enum import Enum
from typing import Annotated, Literal
import random

from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, AfterValidator, Field, HttpUrl


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, description="The description of the item", max_length=300
    )
    price: float = Field(
        gt=0, description="The price must be greater than 0"
    )
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image]


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


app = FastAPI()


data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError(
            'Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id


@app.get("/")
async def root():
    return {
        "message": "Hello World"
    }


@app.post('/offers/')
async def create_offer(offer: Offer):
    return offer


@app.get('/items/')
async def read_item(
    filter_query: Annotated[FilterParams, Query()],
    # id: Annotated[str | None, AfterValidator(check_valid_id)] = None
):

    # if id:
    #     name = data.get(id)
    # else:
    #     id, name = random.choice(list(data.items()))

    # return {
    #     'id': id,
    #     'name': name
    # }

    return filter_query


@app.post('/items/')
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({
            'price_with_tax': price_with_tax
        })

    return item_dict


@app.get('/items/{item_id}')
async def read_item(
    item_id: Annotated[int, Path(description="The ID of the item to get", gt=0, le=100)],
    q: Annotated[str | None, Query(alias='item-query')] = None
):
    results = {
        'item_id': item_id,
    }

    if q:
        results.update({"q": q})

    return results


@app.put('/items/{item_id}')
async def update_item(item_id: int, item: Item, user: User):
    results = {
        'item_id': item_id,
        'item': item,
        'user': user
    }

    return results


@app.get('/models/{model_name}')
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {
            "model_name": model_name,
            "message": "This is the AlexNet model."
        }

    if model_name.value == "lenet":
        return {
            "model_name": model_name,
            "message": "This is the LeCNN model."
        }

    return {
        "model_name": model_name,
        "message": "This is the ResNet model."
    }
