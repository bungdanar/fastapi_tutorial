from typing import Annotated
import random
from uuid import UUID

from fastapi import FastAPI, Query, Path, Body, Cookie, Header
from pydantic import AfterValidator

from models import CommonHeaders, Cookies, FilterParams, Item, ModelName, Offer


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
    cookies: Annotated[Cookies, Cookie()],
    headers: Annotated[CommonHeaders, Header()],
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
    results = filter_query.model_dump()
    results.update({"cookies": cookies.model_dump()})
    results.update({"headers": headers.model_dump()})

    return results


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
async def update_item(item_id: UUID, item: Annotated[Item, Body(
    openapi_examples={
        "normal": {
            "summary": "A normal example",
            "description": "A **normal** item works correctly.",
            "value": {
                "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
            },
        },
        "converted": {
            "summary": "An example with converted data",
            "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
            "value": {
                "name": "Bar",
                        "price": "35.4",
            },
        },
        "invalid": {
            "summary": "Invalid data is rejected with an error",
            "value": {
                "name": "Baz",
                        "price": "thirty five point four",
            },
        },
    },
)]):
    results = {
        'item_id': item_id,
        'item': item,
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
