from typing import Any, Protocol, Optional
from dataclasses import dataclass, field

from silvanus.strategy.routers.base import RouterIteratorProtocol


@dataclass(slots=True, kw_only=True)
class RoutingData:
    app_data: dict[str, Any] = field(default_factory=dict)
    request_data: dict[str, Any] = field(default_factory=dict)
    middleware_data: dict[str, Any] = field(default_factory=dict)
    filters_data: dict[str, Any] = field(default_factory=dict)

    used_filters: dict["FilterProtocol", bool] = field(default_factory=dict)
    used_middlewares: set["MiddlewareProtocol"] = field(default_factory=set)
    inner_middlewares: set["MiddlewareProtocol"] = field(default_factory=set)


@dataclass(slots=True, kw_only=True)
class RouterSchema:
    name: str
    router: "RouterProtocol"
    filters: list["FilterProtocol"]
    middlewares: list["MiddlewareProtocol"]
    children: list["RouterSchema"]
    parent: Optional["RouterSchema"] = None


class FilterProtocol(Protocol):
    async def __call__(self, data: RoutingData) -> bool:
        raise NotImplementedError()

    def __hash__(self) -> int:
        raise NotImplementedError()

    def __eq__(self, other):
        raise NotImplementedError()


class MiddlewareProtocol(Protocol):
    async def __call__(self, data: RoutingData):
        raise NotImplementedError()

    def __hash__(self) -> int:
        raise NotImplementedError()

    def __eq__(self, other):
        raise NotImplementedError()


@dataclass(slots=True, kw_only=True)
class RouterProtocol(Protocol):
    # noinspection PyUnusedLocal
    def __init__(
            self,
            filters: Optional[list[FilterProtocol]] = None,
            middlewares: Optional[list[MiddlewareProtocol]] = None,
            inner_middlewares: Optional[list[MiddlewareProtocol]] = None,
            data: Any = None,
            parent: Optional["RouterProtocol"] = None,
            name: Optional[str] = None
    ):
        """
        Creating a router. A router can be either a direct performer of
        filters or a parent of other routers, depending on the implementation.
        :param data:
        :param filters:
        :param middlewares:
        """
        raise NotImplementedError()

    def add_filter(self, filter_: FilterProtocol):
        """
        Adds a filter to the router
        :param filter_:
        :return:
        """
        raise NotImplementedError()

    def add_router(self, router: "RouterProtocol"):
        """
        Adds a router to the router
        :param router:
        :return:
        """
        raise NotImplementedError()

    def add_routers(self, router: list["RouterProtocol"]):
        """
        Adds a routers to the router
        :param router:
        :return:
        """
        raise NotImplementedError()

    def add_middleware(self, middleware: MiddlewareProtocol, inner: bool = False):
        """
        Adds a middleware to the router
        :param inner:
        :param middleware:
        :return:
        """
        raise NotImplementedError()

    async def route(
            self,
            data: RoutingData,
            iterator: RouterIteratorProtocol
    ) -> Any:
        """
        Search for data by yourself. It can also search through its
        child routers, depending on the execution.
        :param iterator: the determinant of which data to return from the routers
        :param data: An instance of the data that will be used for routing
        and adding data to the data
        :return:
        """
        raise NotImplementedError()

    def get_routers_schema(self, with_parents: bool = False) -> RouterSchema:
        """
        Returns the router diagram, which may be different
        depending on the implementation
        :return:
        """
        raise NotImplementedError()
