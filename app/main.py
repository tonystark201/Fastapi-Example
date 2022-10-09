# * coding:utf-8 *


import click
from app.routers import others, students, users
from common.exception import FastAPIError, InternalError
from common.logs import default_logger
from common.token import Token
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from fastapi import Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError


def create_app() -> FastAPI:
    app = FastAPI()
    app.logger = default_logger
    return app


app = create_app()


class MiddleWare(object):
    def __init__(self, app: ASGIApp):
        self.app = app

    async def authetication(self, request: Request, call_next):
        def is_pass(request: Request):
            whitelist = ["/users/login", ""]
            if request.scope.get("path") in whitelist:
                return True
            return False

        if is_pass(request):
            response: Response = await call_next(request)
            return response
        else:
            token = request.cookies.get("auth_token", None)
            if token:
                user_id = await Token(token=token).get_user_id()
                if not user_id:
                    return JSONResponse(
                        FastAPIError(1001).body,
                        status_code=status.HTTP_401_UNAUTHORIZED,
                    )
                request.app.extra["user_id"] = user_id
                response: Response = await call_next(request)
                if response.status_code not in [401, 404, 400, 500]:
                    response.status_code = status.HTTP_200_OK
                response.status_code = status.HTTP_200_OK
                return response
            else:
                return JSONResponse(
                    FastAPIError(1001).body, status_code=status.HTTP_401_UNAUTHORIZED
                )

    class DummyNativeMiddleware(object):
        def __init__(self, app: ASGIApp):
            app.middleware("http")(self)

        async def __call__(self, request: Request, call_next):
            print("Dummy native middleware: do anyting before handle request")
            response = await call_next(request)
            print("Dummy native middleware: do anyting before flush response")
            return response

    class DummyStarletteMiddleware(object):
        def __init__(self, app: ASGIApp, anything: str = "anything"):
            self.app = app
            self.anything = anything

        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            if scope["type"] == "http":
                print(
                    f"Dummy asgi middleware: do {self.anything} before handle request"
                )
                await self.app(scope, receive, send)
                print(
                    f"Dummy asgi middleware: do {self.anything} before handle request"
                )
            else:
                await self.app(scope, receive, send)

    def register(self):
        self.app.middleware("http")(self.authetication)
        MiddleWare.DummyNativeMiddleware(self.app)
        self.app.add_middleware(MiddleWare.DummyStarletteMiddleware, anything="haha")


MiddleWare(app).register()


class ExceptionHandler(object):
    def __init__(self, app):
        self.app = app

    async def fastapi_error(self, request, exc):
        return JSONResponse(
            content=jsonable_encoder(exc.body), status_code=status.HTTP_400_BAD_REQUEST
        )

    async def internal_error(self, request, exc):
        return JSONResponse(
            content=jsonable_encoder(InternalError(exc).body),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    async def http_error(self, request, exc):

        return JSONResponse(
            content=jsonable_encoder(
                FastAPIError(1005, getattr(exc, "detail", None)).body
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    async def validation_error(self, request, exc):
        err = exc.errors()[0]
        return JSONResponse(
            content=jsonable_encoder(FastAPIError(1004, err.get("msg", None)).body),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    def register(self):
        self.app.exception_handler(FastAPIError)(self.fastapi_error)
        self.app.exception_handler(Exception)(self.internal_error)
        self.app.exception_handler(HTTPException)(self.http_error)
        self.app.exception_handler(RequestValidationError)(self.validation_error)


ExceptionHandler(app).register()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(others.router, prefix="/others", tags=["others"])
app.include_router(students.router, prefix="/stu", tags=["stu"])


@click.command()
@click.option("-h", "--host", "host", default="127.0.0.1", show_default=True)
@click.option("-p", "--port", "port", default=8080, show_default=True)
def main(host, port, app=app):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
