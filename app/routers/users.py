# * coding:utf-8 *
import json
from typing import List

from app.depends import UserDepends
from common.exception import FastAPIError
from common.orms import UserORM
from common.schema import UserModel
from common.token import Token
from starlette.requests import Request
from starlette.responses import Response

from fastapi import APIRouter, Depends, status

router = APIRouter()


@router.post("/login")
async def login(user: UserModel):
    user_id = UserORM.user_login(user)
    if not user_id:
        raise FastAPIError(code=1002)
    tok = Token(user_id=user_id)
    token = await tok.get_token()
    res = Response(status_code=status.HTTP_200_OK)
    res.set_cookie(key="auth_token", value=token)
    return res


@router.post("/logout")
async def logout(request: Request):
    user_id = request.app.extra.get("user_id", None)
    if user_id:
        tok = Token(user_id=user_id)
        await tok.clear()
    return Response(status_code=status.HTTP_200_OK)


@router.post("/", dependencies=[Depends(UserDepends.name_duplicated)])
async def create_user(user: UserModel):
    user_id = UserORM.create_user(user)
    return Response(json.dumps(user_id),status_code=status.HTTP_201_CREATED)


@router.post("/bulk", dependencies=[Depends(UserDepends.bluk_name_duplicated)])
async def create_users(users: List[UserModel]):
    UserORM.create_users(users)
    return Response(status_code=status.HTTP_201_CREATED)


@router.put("/{user_id}", dependencies=[Depends(UserDepends.name_duplicated)])
async def update_user(user_id: str, user: UserModel):
    UserORM.update_user(user_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    UserORM.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
