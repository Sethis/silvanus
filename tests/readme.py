from dataclasses import dataclass

from silvanus.routing.simple import SimpleRouter
from silvanus.strategy.routers import FirstTrueRouterIterator, AllTrueRouterIterator
from silvanus.structures import RoutingData


@dataclass(frozen=True)
class SimpleFilter:  # Our custom simple filter
    value: int

    async def __call__(self, data: RoutingData) -> bool:
        return data.request_data.get("value", None) == self.value


# silvanus supports all data types as a result of routing,
# but the most useful for frameworks will be the return of functions.
def some_handler(text: str) -> str:
    return text * 2


router = SimpleRouter()

router1 = SimpleRouter([SimpleFilter(value=10)], data="wrong")

router2 = SimpleRouter([SimpleFilter(value=15), ], data=some_handler)
router3 = SimpleRouter([SimpleFilter(value=15), ], data="yes!")

router.add_routers([router1, router2, router3])


async def test_main():
    result = await router.route(
        data=RoutingData(
            request_data={"value": 15}
        ),
        iterator=FirstTrueRouterIterator()  # get only first True result
    )

    assert result("silvanus-") == "silvanus-silvanus-"  # our some_handler

    result_2 = await router.route(
        data=RoutingData(
            request_data={"value": 15}
        ),
        iterator=AllTrueRouterIterator()  # get all True result
    )

    assert result_2[0](result_2[1]) == "yes!yes!"  # our some_handler and text from second data
