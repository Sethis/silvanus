

from typing import Optional, Callable, Any, get_type_hints

from .node import Node
from plastic.enums.http import Methods


class Router:
    nodes: dict[str, Node]
    _prefix: Optional[str]

    def __init__(self, prefix: str = ""):
        self.nodes = {}
        self.prefix = prefix

    def _get_node_by_method(self, method) -> Node:
        self_node = self.nodes.get(method)

        if not self_node:
            self_node = Node("")
            self.nodes[method] = self_node

        return self_node

    def include_router(self, router: "Router"):
        items = router.nodes.items()

        for method, node in items:
            self_node = self._get_node_by_method(method)

            self_node.include_node(node)

    def include_routers(self, routers: list["Router"]):
        for i in routers:
            self.include_router(i)

    def sort(self):
        for node in self.nodes.values():
            node.sort()

    def register_method(self, method: str, path: str, handler: Callable, variable_types: dict[str, Any]):
        self_node = self._get_node_by_method(method)

        path = f"{self.prefix}{path}"

        self_node.add_child(
            path=path,
            variable_types=variable_types,
            func=handler
        )

    def register_get(self, path: str, handler: Callable, variable_types: dict[str, Any]):
        self.register_method(Methods.GET, path, handler, variable_types)

    def register_head(self, path: str, handler: Callable, variable_types: dict[str, Any]):
        self.register_method(Methods.HEAD, path, handler, variable_types)

    def register_post(self, path: str, handler: Callable, variable_types: dict[str, Any]):
        self.register_method(Methods.POST, path, handler, variable_types)

    def register_put(self, path: str, handler: Callable, variable_types: dict[str, Any]):
        self.register_method(Methods.PUT, path, handler, variable_types)

    def register_delete(self, path: str, handler: Callable, variable_types: dict[str, Any]):
        self.register_method(Methods.DELETE, path, handler, variable_types)

    def register_options(self, path: str, handler: Callable, variable_types: dict[str, Any]):
        self.register_method(Methods.OPTIONS, path, handler, variable_types)

    def register_trace(self, path: str, handler: Callable, variable_types: dict[str, Any]):
        self.register_method(Methods.TRACE, path, handler, variable_types)

    def register_patch(self, path: str, handler: Callable, variable_types: dict[str, Any]):
        self.register_method(Methods.PATCH, path, handler, variable_types)

    def get(self, path: str):
        def wrapper(func):
            var_types = get_type_hints(func)

            self.register_get(path, func, var_types)

            return func

        return wrapper

    def head(self, path: str):
        def wrapper(func):
            var_types = get_type_hints(func)

            self.register_head(path, func, var_types)

            return func

        return wrapper

    def post(self, path: str):
        def wrapper(func):
            var_types = get_type_hints(func)

            self.register_post(path, func, var_types)

            return func

        return wrapper

    def put(self, path: str):
        def wrapper(func):
            var_types = get_type_hints(func)

            self.register_put(path, func, var_types)

            return func

        return wrapper

    def delete(self, path: str):
        def wrapper(func):
            var_types = get_type_hints(func)

            self.register_delete(path, func, var_types)

            return func

        return wrapper

    def options(self, path: str):
        def wrapper(func):
            var_types = get_type_hints(func)

            self.register_options(path, func, var_types)

            return func

        return wrapper

    def trace(self, path: str):
        def wrapper(func):
            var_types = get_type_hints(func)

            self.register_trace(path, func, var_types)

            return func

        return wrapper

    def patch(self, path: str):
        def wrapper(func):
            var_types = get_type_hints(func)

            self.register_patch(path, func, var_types)

            return func

        return wrapper

    def route(self, method: str, path: str) -> tuple[Callable, list]:
        node = self._get_node_by_method(method)

        return node.get_handler_by_path(path)

