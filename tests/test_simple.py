import copy

from dataclasses import dataclass

from silvanus.routing.simple import SimpleRouter
from silvanus.structures.base import RoutingData
from silvanus.strategy.routers import FirstTrueRouterIterator, AllTrueRouterIterator


class SimpleFilter:
    async def __call__(self, data: RoutingData) -> bool:
        used = data.filters_data.get("used", 0) + 1
        data.filters_data["used"] = used

        return data.request_data["simple"] is True

    def __hash__(self) -> int:
        return hash(type(self))

    def __eq__(self, other):
        return isinstance(other, SimpleFilter)


@dataclass(slots=True, frozen=True, kw_only=True)
class DataclassFilter:
    num: int
    string: str
    iteration: int = 0

    async def __call__(self, data: RoutingData) -> bool:
        used = data.filters_data.get("used", 0) + 1
        data.filters_data["used"] = used

        return (
                data.request_data["num"] == self.num
                and data.request_data["string"] == self.string
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class ChangeDataMiddleware:
    simple: bool
    num: int
    string: str

    async def __call__(self, data: RoutingData):
        data.request_data.update(simple=self.simple, num=self.num, string=self.string)


def test_simple_router_init():
    assert SimpleRouter()


async def test_empty_router():
    data = RoutingData()
    data_2 = copy.deepcopy(data)

    router = SimpleRouter(data="result_data")
    result = await router.route(data_2, FirstTrueRouterIterator())

    assert result == "result_data"
    assert data_2 == data


async def test_nested_router():
    data = RoutingData()
    data_2 = copy.deepcopy(data)

    router = SimpleRouter(data="result1")
    router.add_router(SimpleRouter(data="result2"))

    result = await router.route(data_2, FirstTrueRouterIterator())

    assert result == "result1"
    assert data_2 == data


async def test_nested_router_all_true():
    data = RoutingData()
    data_2 = copy.deepcopy(data)

    router = SimpleRouter(data="result1")
    router.add_router(SimpleRouter(data="result2"))

    result = await router.route(data_2, AllTrueRouterIterator())

    assert result == ["result1", "result2"]
    assert data_2 == data


async def test_nested_router_all_true_one_none():
    data = RoutingData()

    router = SimpleRouter(data=None)
    router.add_router(SimpleRouter(data="result2"))

    data_2 = copy.deepcopy(data)
    result = await router.route(data_2, AllTrueRouterIterator())

    assert result == ["result2"]
    assert data_2 == data

async def test_nested_router_all_true_all_none():
    data = RoutingData()

    router = SimpleRouter(data=None)
    router.add_router(SimpleRouter(data=None))

    data_2 = copy.deepcopy(data)
    result = await router.route(data_2, AllTrueRouterIterator())

    assert result == []
    assert data_2 == data


async def test_router_with_filter():
    data_1 = RoutingData(
            request_data={"simple": True}
        )

    data_2 = RoutingData(
            request_data={"simple": False}
        )

    router = SimpleRouter(
        data="filtered",
        filters=[SimpleFilter(), ]
    )

    result1 = await router.route(
        data=data_1,
        iterator=FirstTrueRouterIterator()
    )

    result2 = await router.route(
        data=data_2,
        iterator=FirstTrueRouterIterator()
    )

    assert result1 == "filtered"
    assert data_1 == RoutingData(
        request_data={"simple": True},
        filters_data={"used": 1},
        used_filters={SimpleFilter(): True}
    )

    assert result2 is None
    assert data_2 == RoutingData(
        request_data={"simple": False},
        filters_data={"used": 1},
        used_filters={SimpleFilter(): False}
    )


async def test_cache_router():
    data_1 = RoutingData(
        request_data={"simple": True}
    )

    data_2 = RoutingData(
        request_data={"simple": False}
    )

    router = SimpleRouter(
        filters=[SimpleFilter(), ]
    )
    router.add_router(
        SimpleRouter(
            data="nested_filtered",
            filters=[SimpleFilter()]
        )
    )

    result1 = await router.route(
        data=data_1,
        iterator=FirstTrueRouterIterator()
    )

    result2 = await router.route(
        data=data_2,
        iterator=FirstTrueRouterIterator()
    )

    assert result1 == "nested_filtered"
    assert data_1 == RoutingData(
        request_data={"simple": True},
        filters_data={"used": 1},
        used_filters={SimpleFilter(): True}
    )

    assert result2 is None
    assert data_2 == RoutingData(
        request_data={"simple": False},
        filters_data={"used": 1},
        used_filters={SimpleFilter(): False}
    )


async def test_dataclass_router():
    data_1 = RoutingData(
            request_data={"num": 123, "string": "test"}
        )

    data_2 = RoutingData(
            request_data={"num": 124, "string": "test"}
        )

    data_3 = RoutingData(
            request_data={"num": 123, "string": "test1"}
        )

    router = SimpleRouter(
        filters=[DataclassFilter(num=123, string="test"), ],
        data="result"
    )

    result1 = await router.route(
        data=data_1,
        iterator=FirstTrueRouterIterator()
    )

    result2 = await router.route(
        data=data_2,
        iterator=FirstTrueRouterIterator()
    )

    result3 = await router.route(
        data=data_3,
        iterator=FirstTrueRouterIterator()
    )

    d_filter = DataclassFilter(
        num=123,
        string="test"
    )

    assert result1 == "result"
    assert data_1 == RoutingData(
        request_data={"num": 123, "string": "test"},
        filters_data={"used": 1},
        used_filters={d_filter: True}
    )

    assert result2 is None
    assert data_2 == RoutingData(
        request_data={"num": 124, "string": "test"},
        filters_data={"used": 1},
        used_filters={d_filter: False}
    )

    assert result3 is None
    assert data_3 == RoutingData(
        request_data={"num": 123, "string": "test1"},
        filters_data={"used": 1},
        used_filters={d_filter: False}
    )


async def long_path_route():
    router = SimpleRouter(
        data="long_data",
        filters=[DataclassFilter(num=123, string="123")]
    )

    parent1 = SimpleRouter(
        filters=[DataclassFilter(num=123, string="123")]
    )
    parent1.add_router(router)

    parent2 = SimpleRouter(
        filters=[SimpleFilter()]
    )
    parent2.add_router(router)

    parent3 = SimpleRouter(
        filters=[SimpleFilter()]
    )
    parent3.add_router(router)

    data = RoutingData(
            request_data={
                "simple": True,
                "num": 123,
                "string": "123"
            }
        )

    result = await parent3.route(
        data=data,
        iterator=FirstTrueRouterIterator()
    )

    assert result == "long_data"
    assert data.filters_data["used"] == 2
    assert data.used_filters == {
        SimpleFilter(): True,
        DataclassFilter(num=123, string="123"): True
    }


async def multi_long_path_route():
    child1 = SimpleRouter(
        data="child1",
        filters=[DataclassFilter(num=123, string="123")]
    )

    parent1 = SimpleRouter(
        filters=[DataclassFilter(num=123, string="123")]
    )
    parent1.add_router(child1)

    child2 = SimpleRouter(
        data="child2",
        filters=[DataclassFilter(num=150, string="text")]
    )

    parent2 = SimpleRouter(
        filters=[SimpleFilter()]
    )
    parent2.add_routers([parent1, child2])

    parent3 = SimpleRouter(
        filters=[SimpleFilter()]
    )
    parent3.add_router(parent3)

    data_1 = RoutingData(
        request_data={
            "simple": True,
            "num": 123,
            "string": "123"
        }
    )

    data_2 = RoutingData(
        request_data={
            "simple": True,
            "num": 150,
            "string": "text"
        }
    )

    result1 = await parent3.route(
        data=data_1,
        iterator=FirstTrueRouterIterator()
    )

    result2 = await parent3.route(
        data=data_2,
        iterator=FirstTrueRouterIterator()
    )

    assert result1 == "child1"
    assert data_1.filters_data["used"] == 2

    assert result2 == "child2"
    assert data_2.filters_data["used"] == 2


async def test_nested_router_with_middleware():
    parent_filter = DataclassFilter(
            num=-100,
            string="another"
        )

    false_filter = DataclassFilter(
        iteration=True,
        num=-100,
        string="another"
            )

    true_filter = DataclassFilter(
                num=200,
                string="different"
            )

    parent = SimpleRouter(
        data=None,
        middlewares=[],
        filters=[parent_filter]
    )
    true_router = SimpleRouter(
        data="true",
        filters=[true_filter, ],
        inner_middlewares=[
            ChangeDataMiddleware(
                simple=False,
                num=1000,
                string="finally"
                )
            ]
        )

    false_router = SimpleRouter(
            data="absolute_false",
            filters=[false_filter, ],
            middlewares=[ChangeDataMiddleware(
                simple=True,
                num=200,
                string="different"
            )],
            inner_middlewares=[
                ChangeDataMiddleware(
                    simple=True,
                    num=-1000,
                    string="break"
                )
            ]
    )

    parent.add_routers([false_router, true_router])

    data = RoutingData(
            request_data={
                "simple": False,
                "num": -100,
                "string": "another"
            }
        )

    result = await parent.route(
        data,
        iterator=FirstTrueRouterIterator()
    )

    assert result == "true"
    assert data == RoutingData(
        request_data={
            "simple": False,
            "num": 1000,
            "string": "finally"
        },
        filters_data={
            "used": 3,
        },
        used_filters={
            parent_filter: True,
            false_filter: False,
            true_filter: True
        },
        used_middlewares={
            ChangeDataMiddleware(
                simple=True,
                num=200,
                string="different"
            ),
        },
        inner_middlewares={
            ChangeDataMiddleware(
                simple=False,
                num=1000,
                string="finally"
            )
        }
    )
