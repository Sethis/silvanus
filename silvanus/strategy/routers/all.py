from typing import Protocol, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from silvanus.structures.base import RouterProtocol, RoutingData


class AllTrueRouterIterator(Protocol):
    def __init__(self):
        self._returned = []
        self._nested = False

    async def __call__(
            self,
            routers: list["RouterProtocol"],
            data: "RoutingData",
            router_data: Any
    ) -> Any:
        nested = self._nested
        self._nested = True

        if router_data:
            self._returned.append(router_data)

        for router in routers:
            result = await router.route(data, self)

            if result is not None:
                self._returned.extend(result)

        if not nested:
            return self._returned

        else:
            return None
