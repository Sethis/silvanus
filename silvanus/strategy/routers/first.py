from typing import Protocol, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from silvanus.structures.base import RouterProtocol, RoutingData


class FirstTrueRouterIterator(Protocol):
    def __init__(self, on_nothing: Any = None):
        self.on_nothing = on_nothing

    async def __call__(
            self,
            routers: list["RouterProtocol"],
            data: "RoutingData",
            router_data: Any
    ) -> Any:
        if router_data:
            return router_data

        for router in routers:
            result = await router.route(data, self)

            if result is not self.on_nothing:
                return result

        return self.on_nothing
