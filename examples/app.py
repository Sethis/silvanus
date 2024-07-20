

from typing import Type, Callable, Any, Optional

from starlette.responses import JSONResponse, PlainTextResponse
from starlette.types import Receive, Scope, Send
from starlette import status

from silvanus import Router
from silvanus.routing.node import Node
from silvanus.enums.http import Methods


class App:
    _router: Router

    def __init__(self, prefix: str = "", node_class: Type[Node] = Node):
        self._router = Router(
            prefix=prefix,
            node_class=node_class
        )
        self._was_sort: bool = False
        # it is undesirable to do this because of performance,
        # this is just to simplify the example

    def include_router(self, router: Router):
        router.sort()

        self._router.include_router(router)

    def include_routers(self, routers: list[Router]):
        for i in routers:
            self.include_router(i)

    def register_get(self, path: str, handler: Callable):
        self._router.register_method(Methods.GET, path, handler)

    def register_head(self, path: str, handler: Callable):
        self._router.register_method(Methods.HEAD, path, handler)

    def register_post(self, path: str, handler: Callable):
        self._router.register_method(Methods.POST, path, handler)

    def register_put(self, path: str, handler: Callable):
        self._router.register_method(Methods.PUT, path, handler)

    def register_delete(self, path: str, handler: Callable):
        self._router.register_method(Methods.DELETE, path, handler)

    def register_options(self, path: str, handler: Callable):
        self._router.register_method(Methods.OPTIONS, path, handler)

    def register_trace(self, path: str, handler: Callable):
        self._router.register_method(Methods.TRACE, path, handler)

    def register_patch(self, path: str, handler: Callable):
        self._router.register_method(Methods.PATCH, path, handler)

    def get(self, path: str):
        return self._router.get(path)

    def head(self, path: str):
        return self._router.get_register_wrapper(Methods.HEAD, path)

    def post(self, path: str):
        return self._router.get_register_wrapper(Methods.POST, path)

    def put(self, path: str):
        return self._router.get_register_wrapper(Methods.PUT, path)

    def delete(self, path: str):
        return self._router.get_register_wrapper(Methods.DELETE, path)

    def options(self, path: str):
        return self._router.get_register_wrapper(Methods.OPTIONS, path)

    def trace(self, path: str):
        return self._router.get_register_wrapper(Methods.TRACE, path)

    def patch(self, path: str):
        return self._router.get_register_wrapper(Methods.PATCH, path)

    @staticmethod
    def _parse_params(params: str) -> dict[str, Any]:
        result = {}

        splitted = params.split("&")

        for query in splitted:
            data = query.split("=")

            if len(data) < 2:
                continue

            result[data[0]] = data[1]

        return result

    async def _handle_request(self, method: str, url: str, params: str) -> str:
        data = self._router.route(method, url)

        handler = data[0]
        arg_data = data[1]

        params_data = self._parse_params(params)

        data = {**arg_data, **params_data}

        try:
            result = await handler(**data)

        except TypeError:
            result = handler(**data)

        return str(result)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if not self._was_sort:
            # it is undesirable to do this because of performance,
            # this is just to simplify the example

            self._router.sort()
            self._was_sort: bool = True

        try:
            assert scope['type'] == 'http'

            method: str = scope["method"]
            url: str = scope["path"]
            params: bytes = scope["query_string"]

            str_params = params.decode("utf-8")

            data = await self._handle_request(method=method, url=url, params=str_params)
            response = PlainTextResponse(data)

            await response(scope, receive, send)

        except Exception as e:
            response = JSONResponse(
                {"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            await response(scope, receive, send)
            raise e


app = App()


@app.get("/{value}")
def root(value: int):
    return value


@app.get("/{value}/sqrt")
def root(value: int, multi: Optional[str] = None):
    if not multi:
        multi = 2

    else:
        multi = int(multi)

    return value ** multi


@app.get("/{text}")
def root(text: str):
    return f'Your text: {text}'


@app.get("/me")
async def root():
    return "hello async world!"


@app.get("/mee")
def root():
    return "hello sync world!"


@app.get("/favicon.ico")
async def root():
    return "It system text"
