from typing import Protocol, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from silvanus.structures.base import RouterProtocol, RoutingData

class RouterIteratorProtocol(Protocol):
    async def __call__(
            self,
            routers: list["RouterProtocol"],
            data: "RoutingData",
            router_data: Any
    ) -> Any:
        raise NotImplemented()
