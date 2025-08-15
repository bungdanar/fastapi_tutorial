from typing import Annotated

from fastapi import Depends, HTTPException, Header
from models import UserIn, UserInDB


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.model_dump(),
                          hashed_password=hashed_password)

    return user_in_db


class CommonQueryParams:
    def __init__(
        self,
        q: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> None:
        self.q = q
        self.skip = skip
        self.limit = limit


CommonsDep = Annotated[CommonQueryParams,
                       Depends(CommonQueryParams, use_cache=True)]


async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != 'fake-super-secret-key':
        raise HTTPException(status_code=400, detail="X-Key header invalid")

    return x_key
