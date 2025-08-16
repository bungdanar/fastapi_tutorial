from typing import Annotated, Any, Union
import random
from uuid import UUID

from fastapi import Depends, FastAPI, Form, Query, Path, Body, Cookie, Header, UploadFile, status, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.params import File
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import AfterValidator

from models import CarItem, CommonHeaders, Cookies, FilterParams, FormData, Item, ModelName, Offer, PlaneItem, Tags, User, UserIn
from utils import CommonsDep, fake_save_user, get_current_user, verify_key, verify_token, oauth2_scheme
from data import items  # Assuming items is defined in database.py


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


app = FastAPI()


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={
            'message': f'Oops! {exc.name} did something. There goes a rainbow...'
        }
    )


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


@app.post('/offers/', tags=[Tags.offers])
async def create_offer(offer: Offer):
    return offer


@app.get('/items/', tags=[Tags.items], )
async def read_items(commons: CommonsDep, token: Annotated[str, Depends(oauth2_scheme)]) -> Any:
    return jsonable_encoder(commons)


@app.post(
    '/items/',
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    tags=[Tags.items],
    summary="Create an item",
    response_description="The created item",
)
async def create_item(item: Item) -> Any:
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """

    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({
            'price_with_tax': price_with_tax
        })

    return Item(**item_dict)


@app.get('/items/{item_id}', tags=[Tags.items])
async def read_item(
    # item_id: Annotated[int, Path(description="The ID of the item to get", gt=0, le=100)],
    item_id: str,
    q: Annotated[str | None, Query(alias='item-query')] = None
):
    if item_id not in items:
        raise HTTPException(status_code=404, detail='Item not found', headers={
                            'X-Error': 'There goes my error'})

    return {
        'item': items[item_id],
    }


@app.put('/items/{item_id}', tags=[Tags.items], response_model=Item)
async def update_item(item_id: str, item: Annotated[Item, Body(
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
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return update_item_encoded


@app.get('/models/{model_name}', tags=[Tags.models])
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


@app.post('/users/', tags=[Tags.users])
async def create_user(user: UserIn):
    user_saved = fake_save_user(user)
    return user_saved


@app.get('/users/me', tags=[Tags.users])
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@app.post('/login/', tags=[Tags.auth])
async def login(data: Annotated[FormData, Form()]):
    return {
        "username": data.username,
        "message": "Login successful"
    }


@app.post('/file/', tags=[Tags.files])
async def create_file(file: Annotated[bytes, File(description='A file read as bytes')]):
    return {
        'file_size': len(file)
    }


@app.post('/files/', tags=[Tags.files])
async def create_files(files: Annotated[list[bytes], File(description='Multiple files as bytes')]):
    return {
        'file_sizes': [len(file) for file in files]
    }


@app.post('/uploadfile/', tags=[Tags.files])
async def create_upload_file(file: Annotated[UploadFile, File(description='A file read as UploadFile')]):
    return {
        'filename': file.filename
    }


@app.post('/uploadfiles/', tags=[Tags.files])
async def create_upload_files(files: Annotated[list[UploadFile], File(description='Multiple files as UploadFile')]):
    return {
        'filenames': [file.filename for file in files]
    }


@app.post('/complex-form/', tags=[Tags.etc])
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


@app.get('/unicorns/{name}', tags=[Tags.etc])
async def read_unicorn(name: str):
    if name == 'yolo':
        raise UnicornException(name=name)
    return {
        'unicorn_name': name
    }
