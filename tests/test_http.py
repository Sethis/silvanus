from silvanus.integration.http import (
    parse_path,
    PathFilter,
    TypeFilter,
    MethodFilter,
    LenghtFilter,
    get_path_filters
)
from silvanus.routing.simple import SimpleRouter
from silvanus.structures.base import RoutingData
from silvanus.strategy.routers import FirstTrueRouterIterator


def test_parsing_simple():
    path = "/simple/path/value/1234/3.14/some"

    response = parse_path(path, app_data={}, method="GET")
    need_resulting = RoutingData(
        request_data={
            "request_len": 7,
            "request_path_strings": ["", "simple", "path", "value", "1234", "3.14", "some"],
            "request_method": "GET"
        }
    )

    assert need_resulting == response


def test_parsing_empty():
    path = "/"

    response = parse_path(path, app_data={}, method="GET")
    need_resulting = RoutingData(
        request_data={
            "request_len": 2,
            "request_path_strings": ["", ""],
            "request_method": "GET"
        }
    )

    assert need_resulting == response


async def test_filtering_path():
    path = "/this/1234"

    response = parse_path(path, app_data={}, method="GET")

    filters = PathFilter(index=0, text="")

    assert (await filters(response)) is True
    assert await filters(response) == await filters(response)

    filters = PathFilter(index=1, text="this")

    assert (await filters(response)) is True
    assert await filters(response) == await filters(response)

    filters = PathFilter(index=2, text="1234")

    assert (await filters(response)) is True
    assert await filters(response) == await filters(response)


async def test_filtering_parsing():
    path = "/path/1234/3.14"

    response = parse_path(path, app_data={}, method="GET")

    filter_result = await PathFilter(index=1, text="path")(response)
    assert filter_result is True

    filter_result = await PathFilter(index=1, text="pathfalse")(response)
    assert filter_result is False

    filter_result = await PathFilter(index=1, text="pa")(response)
    assert filter_result is False

    filter_result = await PathFilter(index=2, text="1234")(response)
    assert filter_result is True

    filter_result = await TypeFilter(index=1, name="result", value_type=float)(response)
    assert filter_result is False
    assert response.filters_data.get("result", None) is None

    filter_result = await TypeFilter(index=1, name="result", value_type=str)(response)
    assert filter_result is True
    assert response.filters_data.get("result", None) == "path"

    filter_result = await TypeFilter(index=2, name="result", value_type=int)(response)
    assert filter_result is True
    assert response.filters_data.get("result", None) == 1234

    filter_result = await TypeFilter(index=2, name="result", value_type=float)(response)
    assert filter_result is True
    assert response.filters_data.get("result", None) == 1234.0

    filter_result = await TypeFilter(index=3, name="result", value_type=int)(response)
    assert filter_result is False

    filter_result = await TypeFilter(index=3, name="result", value_type=float)(response)
    assert filter_result is True
    assert response.filters_data.get("result", None) == 3.14


async def test_filter_getter():
    path = "/user/{name: str}/{age:int}/{height : float}/{var}/{string}"

    filters = get_path_filters(path, {"var": int}, method="GET")

    assert filters == [
        MethodFilter(method="GET"),
        LenghtFilter(lenght=7),
        PathFilter(index=1, text="user"),
        TypeFilter(index=2, name="name", value_type=str),
        TypeFilter(index=3, name="age", value_type=int),
        TypeFilter(index=4, name="height", value_type=float),
        TypeFilter(index=5, name="var", value_type=int),
        TypeFilter(index=6, name="string", value_type=str)
    ]

    response = "/user/timmy/10/10.1/1/10"
    data = parse_path(response, app_data={}, method="GET")

    for filter_ in filters:
        assert (await filter_(data)) is True


async def test_filter_routing():
    path = "/user/{name: str}/{age:int}/{height : float}/{var}/{string}"

    filters = get_path_filters(path, {"var": int}, method="GET")

    response = "/user/timmy/10/10.1/1/10"
    data = parse_path(response, app_data={"name": "tommy"}, method="GET")

    handler = SimpleRouter(
        filters=filters,
        data="true_result"
    )

    root_router = SimpleRouter()
    root_router.add_router(handler)

    result = await root_router.route(data=data, iterator=FirstTrueRouterIterator())

    assert result == "true_result"
    assert data.filters_data == {
                "name": "timmy",
                "age": 10,
                "height": 10.1,
                "var": 1,
                "string": "10"
            }

    assert data.app_data["name"] == "tommy"


async def test_filter_routing_different_method():
    path = "/user/{name: str}/{age:int}/{height : float}/{var}/{string}"

    filters = get_path_filters(path, {"var": int}, method="GET")

    response = "/user/timmy/10/10.1/1/10"
    data = parse_path(response, app_data={"name": "tommy"}, method="POST")

    handler = SimpleRouter(
        filters=filters,
        data="true_result"
    )

    root_router = SimpleRouter()
    root_router.add_router(handler)

    result = await root_router.route(data=data, iterator=FirstTrueRouterIterator())

    assert result is None
    assert data.filters_data == {}

    assert data.app_data["name"] == "tommy"
