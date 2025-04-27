

from typing import Any, Optional

from silvanus.structures.base import (
    RoutingData,
    BaseFilter,
    BaseMiddleware,
    RouterSchema,
    BaseRouter
)


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
            filters: Optional[list[BaseFilter]] = None,
            middlewares: Optional[list[BaseMiddleware]] = None,
            inner_middlewares: Optional[list[BaseMiddleware]] = None,
            data: Any = None,
            parent: Optional["BaseRouter"] = None,
            name: Optional[str] = None
    ):
        if not name:
            name = f"{__name__}"

        self.name = name
        self.data = data
        self.routers: list[BaseRouter] = []

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

    def add_filter(self, filter_: BaseFilter):
        self.filters.append(filter_)

    def add_middleware(self, middleware: BaseMiddleware, inner: bool = False):
        if inner:
            self.inner_middlewares.append(middleware)
            return

        self.middlewares.append(middleware)

    def add_router(self, router: "BaseRouter"):
        self.routers.append(router)

    def add_routers(self, routers: list["BaseRouter"]):
        self.routers.extend(routers)

    async def route(self, data: RoutingData) -> tuple[Any, RoutingData]:
        for middleware in self.middlewares:
            if middleware not in data.used_middlewares:
                await middleware(data)
                data.used_middlewares.add(middleware)

        for self_filter in self.filters:
            filter_result = data.used_filters.get(self_filter, None)

            if filter_result is not None:
                if not filter_result:
                    return None, data

                continue

            filter_result = await self_filter(data)
            data.used_filters[self_filter] = filter_result

            if not filter_result:
                return None, data

        for inner in self.inner_middlewares:
            data.inner_middlewares.add(inner)

        for self_router in self.routers:
            result = await self_router.route(data)

            if result[0] is not None:
                return result

        for inner in data.inner_middlewares:
            await inner(data)

        return self.data, data

    def get_routers_schema(self, with_parents: bool = False) -> RouterSchema:
        childrens = []

        parent = None

        if with_parents and self.parent:
            parent = self.parent.get_routers_schema(with_parents=True)

        for children in self.routers:
            childrens.append(children.get_routers_schema())

        return RouterSchema(
            name=self.name,
            router=self,
            filters=self.filters,
            middlewares=self.middlewares,
            children=childrens,
            parent=parent
        )
