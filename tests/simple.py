

import copy

from dataclasses import dataclass

from silvanus.routing.simple import SimpleRouter
from silvanus.structures.base import RoutingData


class SimpleFilter:
    async def __call__(self, data: RoutingData) -> [bool, RoutingData]:
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

    async def __call__(self, data: RoutingData) -> [bool, RoutingData]:
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


def test_simpe_router_init():
    assert SimpleRouter()


async def test_empty_router():
    data = RoutingData()

    router = SimpleRouter(data="result_data")
    result = await router.route(copy.deepcopy(data))

    assert result[0] == "result_data"
    assert result[1] == data


async def test_nested_router():
    data = RoutingData()

    router = SimpleRouter(data="result1")
    router.add_router(SimpleRouter(data="result2"))

    result = await router.route(copy.deepcopy(data))

    assert result[0] == "result2"
    assert result[1] == data


async def test_router_with_filter():
    router = SimpleRouter(
        data="filtered",
        filters=[SimpleFilter(), ]
    )

    result1 = await router.route(
        data=RoutingData(
            request_data={"simple": True}
        )
    )

    result2 = await router.route(
        data=RoutingData(
            request_data={"simple": False}
        )
    )

    assert result1[0] == "filtered"
    assert result1[1] == RoutingData(
        request_data={"simple": True},
        filters_data={"used": 1},
        used_filters={SimpleFilter(): True}
    )

    assert result2[0] is None
    assert result2[1] == RoutingData(
        request_data={"simple": False},
        filters_data={"used": 1},
        used_filters={SimpleFilter(): False}
    )


async def test_cache_router():
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
        data=RoutingData(
            request_data={"simple": True}
        )
    )

    result2 = await router.route(
        data=RoutingData(
            request_data={"simple": False}
        )
    )

    assert result1[0] == "nested_filtered"
    assert result1[1] == RoutingData(
        request_data={"simple": True},
        filters_data={"used": 1},
        used_filters={SimpleFilter(): True}
    )

    assert result2[0] is None
    assert result2[1] == RoutingData(
        request_data={"simple": False},
        filters_data={"used": 1},
        used_filters={SimpleFilter(): False}
    )


async def test_dataclass_router():
    router = SimpleRouter(
        filters=[DataclassFilter(num=123, string="test"), ],
        data="result"
    )

    result1 = await router.route(
        data=RoutingData(
            request_data={"num": 123, "string": "test"}
        )
    )

    result2 = await router.route(
        data=RoutingData(
            request_data={"num": 124, "string": "test"}
        )
    )

    result3 = await router.route(
        data=RoutingData(
            request_data={"num": 123, "string": "test1"}
        )
    )

    d_filter = DataclassFilter(
        num=123,
        string="test"
    )

    assert result1[0] == "result"
    assert result1[1] == RoutingData(
        request_data={"num": 123, "string": "test"},
        filters_data={"used": 1},
        used_filters={d_filter: True}
    )

    assert result2[0] is None
    assert result2[1] == RoutingData(
        request_data={"num": 124, "string": "test"},
        filters_data={"used": 1},
        used_filters={d_filter: False}
    )

    assert result3[0] is None
    assert result3[1] == RoutingData(
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

    result = await parent3.route(
        data=RoutingData(
            request_data={
                "simple": True,
                "num": 123,
                "string": "123"
            }
        )
    )

    assert result[0] == "long_data"
    assert result[1].filters_data["used"] == 2
    assert result[1].used_filters == {
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

    result1 = await parent3.route(
        data=RoutingData(
            request_data={
                "simple": True,
                "num": 123,
                "string": "123"
            }
        )
    )

    result2 = await parent3.route(
        data=RoutingData(
            request_data={
                "simple": True,
                "num": 150,
                "string": "text"
            }
        )
    )

    assert result1[0] == "child1"
    assert result1[1].filters_data["used"] == 2

    assert result2[0] == "child2"
    assert result2[1].filters_data["used"] == 2


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
        data="notrue",
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

    result = await parent.route(
        RoutingData(
            request_data={
                "simple": False,
                "num": -100,
                "string": "another"
            }
        )
    )

    assert result[0] == "true"
    assert result[1] == RoutingData(
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
