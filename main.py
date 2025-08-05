from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel


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


fake_items_db = [{"item_name": "Foo"}, {
    "item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/")
async def root():
    return {
        "message": "Hello World"
    }


@app.get('/items/')
async def read_item(skip: int, limit: int = 10):
    return fake_items_db[skip: skip + limit]


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
