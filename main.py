from enum import Enum
from typing import Annotated
import random

from fastapi import FastAPI, Query
from pydantic import BaseModel, AfterValidator


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


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


@app.get('/items/')
async def read_item(
    skip: int = 0,
    limit: int = 10,
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None
):

    if id:
        name = data.get(id)
    else:
        id, name = random.choice(list(data.items()))

    return {
        'id': id,
        'name': name
    }


@app.post('/items/')
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({
            'price_with_tax': price_with_tax
        })

    return item_dict


@app.put('/items/{item_id}')
async def update_item(item_id: int, item: Item):
    return {
        "item_id": item_id,
        **item.model_dump()
    }


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
