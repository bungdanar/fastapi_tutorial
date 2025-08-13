from typing import Annotated, Any, Union
import random
from uuid import UUID

from fastapi import FastAPI, Form, Query, Path, Body, Cookie, Header, UploadFile, status
from fastapi.params import File
from pydantic import AfterValidator

from models import CarItem, CommonHeaders, Cookies, FilterParams, FormData, Item, ModelName, Offer, PlaneItem, UserIn
from utils import fake_save_user
from data import items  # Assuming items is defined in database.py


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


@app.get('/items/', response_model=list[Item])
async def read_items(
    filter_query: Annotated[FilterParams, Query()],
    cookies: Annotated[Cookies, Cookie()],
    headers: Annotated[CommonHeaders, Header()],
    # id: Annotated[str | None, AfterValidator(check_valid_id)] = None
) -> Any:

    # if id:
    #     name = data.get(id)
    # else:
    #     id, name = random.choice(list(data.items()))

    # return {
    #     'id': id,
    #     'name': name
    # }
    # results = filter_query.model_dump()
    # results.update({"cookies": cookies.model_dump()})
    # results.update({"headers": headers.model_dump()})

    # return results

    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]


@app.post('/items/', response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item) -> Any:
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({
            'price_with_tax': price_with_tax
        })

    return Item(**item_dict)


@app.get('/items/{item_id}', response_model=Union[PlaneItem, CarItem])
async def read_item(
    # item_id: Annotated[int, Path(description="The ID of the item to get", gt=0, le=100)],
    item_id: str,
    q: Annotated[str | None, Query(alias='item-query')] = None
):

    return items[item_id]


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


@app.post('/users/')
async def create_user(user: UserIn):
    user_saved = fake_save_user(user)
    return user_saved


@app.post('/login/')
async def login(data: Annotated[FormData, Form()]):
    return {
        "username": data.username,
        "message": "Login successful"
    }


@app.post('/file/')
async def create_file(file: Annotated[bytes, File(description='A file read as bytes')]):
    return {
        'file_size': len(file)
    }


@app.post('/files/')
async def create_files(files: Annotated[list[bytes], File(description='Multiple files as bytes')]):
    return {
        'file_sizes': [len(file) for file in files]
    }


@app.post('/uploadfile/')
async def create_upload_file(file: Annotated[UploadFile, File(description='A file read as UploadFile')]):
    return {
        'filename': file.filename
    }


@app.post('/uploadfiles/')
async def create_upload_files(files: Annotated[list[UploadFile], File(description='Multiple files as UploadFile')]):
    return {
        'filenames': [file.filename for file in files]
    }


@app.post('/complex-form/')
async def create_complex_form(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    return {
        'file_size': len(file),
        'fileb_content_type': fileb.content_type,
        'username': username,
        'password': password
    }
