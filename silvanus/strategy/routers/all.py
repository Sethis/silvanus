from typing import Protocol, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from silvanus.structures.base import RouterProtocol, RoutingData


class AllTrueRouterIterator(Protocol):
    def __init__(self, on_nothing: Any = None):
        self._returned = []
        self._nested = False
        self._on_nothing = on_nothing

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

            if result is not self._on_nothing:
                self._returned.extend(result)

        if not nested:
            return self._returned

        else:
            return self._on_nothing
