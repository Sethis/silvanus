

import asyncio
from dataclasses import dataclass

from silvanus.integration.http import get_path_filters, parse_path
from silvanus.routing.simple import SimpleRouter
from silvanus.structures.base import RoutingData


simple_path = "/user/{id:int}/profile/{full:str}"


SimleDataBase = {
    1: "tommy"
}


@dataclass(frozen=True)
class DatabaseMiddleware:
    async def __call__(self, data: RoutingData):
        try:
            user_id = data.filters_data["id"]
            user_name = data.app_data["database"].get(user_id, None)
            data.middleware_data["user"] = (user_id, user_name)

        except KeyError:
            data.middleware_data["user"] = None


@dataclass(frozen=True)
class TextMiddleware:
    text: str

    async def __call__(self, data: RoutingData):
        data.middleware_data["text"] = self.text


async def simple_handler(id: int, full: str, user: tuple[int, str], text: str) -> str:
    if not user[1] == "tommy":
        return "you are not my tommy!"

    if not user[0] == id:
        return "who are you"

    if not full == "yes":
        return "only full!"

    return f"tommy, {text}!"


simple_handler_router = SimpleRouter(
    filters=get_path_filters(simple_path, method="GET", param_types={}),
    data=simple_handler,
    name="simple_handler"
)


other_path = "/user/{number:int}"


async def other_handler(number: int, text: str) -> bool:
    return number == 2 and text == "hello"


other_hanler_router = SimpleRouter(
    filters=get_path_filters(other_path, method="GET", param_types={}),
    data=other_handler,
    name="other_handler"
)


root_router = SimpleRouter()
root_router.add_routers(
    [
        simple_handler_router,
        other_hanler_router
    ]
)

root_router.add_middleware(
    middleware=TextMiddleware(text="hello")
)
root_router.add_middleware(
    middleware=DatabaseMiddleware(),
    inner=True
)


async def main():
    handler, data = await root_router.route(
        data=parse_path("/user/2", method="GET", app_data={"database": SimleDataBase})
    )

    result = await handler(
        data.filters_data["number"],
        data.middleware_data["text"]
    )
    assert result is True

    handler, data = await root_router.route(
        data=parse_path("/user/1/profile/yes", method="GET", app_data={"database": SimleDataBase})
    )

    result = await handler(
        data.filters_data["id"],
        data.filters_data["full"],
        data.middleware_data["user"],
        data.middleware_data["text"]
    )
    assert result == "tommy, hello!"

    schema = root_router.get_routers_schema()
    print(schema)
    # RouterSchema(name='silvanus.routing.simple', router=<silvanus.routing.simple.SimpleRouter object at
    # 0x000002FA84D577C0>, filters=[], middlewares=[TextMiddleware(text='hello')],
    # children=[RouterSchema(name='simple_handler', router=<silvanus.routing.simple.SimpleRouter object at
    # 0x000002FA82766B60>, filters=[MethodFilter(method='GET'), LenghtFilter(lenght=5),
    # PathFilter(index=1, text='user'), TypeFilter(index=2, name='id', value_type=<class 'int'>), PathFilter(index=3,
    # text='profile'), TypeFilter(index=4, name='full', value_type=<class 'str'>)], middlewares=[],
    # children=[], parent=None), RouterSchema(name='other_handler',
    # router=<silvanus.routing.simple.SimpleRouter object at 0x000002FA84D57820>, filters=[MethodFilter(method='GET'),
    # LenghtFilter(lenght=3), PathFilter(index=1, text='user'),
    # TypeFilter(index=2, name='number', value_type=<class 'int'>)],
    # middlewares=[], children=[], parent=None)], parent=None)


asyncio.run(main())
