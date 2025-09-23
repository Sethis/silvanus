from typing import Any, Optional

from silvanus.structures.base import (
    RoutingData,
    FilterProtocol,
    MiddlewareProtocol,
    RouterSchema,
    RouterProtocol
)

from silvanus.strategy.routers.base import RouterIteratorProtocol


__all__ = ["SimpleRouter", ]


class SimpleRouter:
    __slots__ = (
        "name",
        "data",
        "routers",
        "filters",
        "parent",
        "middlewares",
        "inner_middlewares"
    )

    def __init__(
            self,
            filters: Optional[list[FilterProtocol]] = None,
            middlewares: Optional[list[MiddlewareProtocol]] = None,
            inner_middlewares: Optional[list[MiddlewareProtocol]] = None,
            data: Any = None,
            parent: Optional["RouterProtocol"] = None,
            name: Optional[str] = None
    ):
        if not name:
            name = f"{__name__}"

        self.name = name
        self.data = data
        self.routers: list[RouterProtocol] = []

        if not filters:
            filters = []

        if not middlewares:
            middlewares = []

        if not inner_middlewares:
            inner_middlewares = []

        self.filters = filters
        self.middlewares = middlewares
        self.inner_middlewares = inner_middlewares
        self.parent = parent

    def add_filter(self, filter_: FilterProtocol):
        self.filters.append(filter_)

    def add_middleware(self, middleware: MiddlewareProtocol, inner: bool = False):
        if inner:
            self.inner_middlewares.append(middleware)
            return

        self.middlewares.append(middleware)

    def add_router(self, router: "RouterProtocol"):
        self.routers.append(router)

    def add_routers(self, routers: list["RouterProtocol"]):
        self.routers.extend(routers)

    async def route(
            self,
            data: RoutingData,
            iterator: RouterIteratorProtocol
    ) -> Any:

        for middleware in self.middlewares:
            if middleware not in data.used_middlewares:
                await middleware(data)
                data.used_middlewares.add(middleware)

        for self_filter in self.filters:
            filter_result = data.used_filters.get(self_filter, None)

            if filter_result is not None:
                if not filter_result:
                    return None

                continue

            filter_result = await self_filter(data)
            data.used_filters[self_filter] = filter_result

            if not filter_result:
                return None

        for inner in self.inner_middlewares:
            data.inner_middlewares.add(inner)

        result = await iterator(self.routers, data, self.data)

        for inner in data.inner_middlewares:
            await inner(data)

        return result

    def get_routers_schema(self, with_parents: bool = False) -> RouterSchema:
        children = []

        parent = None

        if with_parents and self.parent:
            parent = self.parent.get_routers_schema(with_parents=True)

        for child in self.routers:
            children.append(child.get_routers_schema())

        return RouterSchema(
            name=self.name,
            router=self,
            filters=self.filters,
            middlewares=self.middlewares,
            children=children,
            parent=parent
        )
