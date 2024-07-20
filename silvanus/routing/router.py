

from typing import Optional, Callable, Any, get_type_hints, Type

from .node import Node
from silvanus.enums.http import Methods


class Router:
    nodes: dict[str, Node]
    _prefix: Optional[str]

    def __init__(self, prefix: str = "", node_class: Type = Node):
        self.nodes = {}
        self.prefix = prefix
        self._node_class = node_class

    def _get_node_by_method(self, method) -> Node:
        self_node = self.nodes.get(method)

        if not self_node:
            self_node = self._node_class("")
            self.nodes[method] = self_node

        return self_node

    def include_router(self, router: "Router"):
        items = router.nodes.items()

        for method, node in items:
            self_node = self._get_node_by_method(method)

            self_node.include_node(node)

    def sort(self):
        for node in self.nodes.values():
            node.sort()

    def _register(self, method: str, path: str, handler: Callable, variable_types: dict[str, Any]):
        self_node = self._get_node_by_method(method)

        path = f"{self.prefix}{path}"

        if len(path) == 0:
            raise ValueError("An empty path to the handler")

        if path[0] == "/":
            path = path[1:]

        self_node.add_child(
            path=path,
            variable_types=variable_types,
            func=handler
        )

    def register_method(self, method: str, path: str, handler: Callable):
        var_types = get_type_hints(handler)

        self._register(method, path, handler, var_types)

    def register_get(self, path: str, handler: Callable):
        self.register_method(Methods.GET, path, handler)

    def register_head(self, path: str, handler: Callable):
        self.register_method(Methods.HEAD, path, handler)

    def register_post(self, path: str, handler: Callable):
        self.register_method(Methods.POST, path, handler)

    def register_put(self, path: str, handler: Callable):
        self.register_method(Methods.PUT, path, handler)

    def register_delete(self, path: str, handler: Callable):
        self.register_method(Methods.DELETE, path, handler)

    def register_options(self, path: str, handler: Callable):
        self.register_method(Methods.OPTIONS, path, handler)

    def register_trace(self, path: str, handler: Callable):
        self.register_method(Methods.TRACE, path, handler)

    def register_patch(self, path: str, handler: Callable):
        self.register_method(Methods.PATCH, path, handler)

    def get_register_wrapper(self, method: str, path: str):
        def wrapper(func):
            self.register_method(method, path, func)

            return func

        return wrapper

    def get(self, path: str):
        return self.get_register_wrapper(Methods.GET, path)

    def head(self, path: str):
        return self.get_register_wrapper(Methods.HEAD, path)

    def post(self, path: str):
        return self.get_register_wrapper(Methods.POST, path)

    def put(self, path: str):
        return self.get_register_wrapper(Methods.PUT, path)

    def delete(self, path: str):
        return self.get_register_wrapper(Methods.DELETE, path)

    def options(self, path: str):
        return self.get_register_wrapper(Methods.OPTIONS, path)

    def trace(self, path: str):
        return self.get_register_wrapper(Methods.TRACE, path)

    def patch(self, path: str):
        return self.get_register_wrapper(Methods.PATCH, path)

    def route(self, method: str, path: str) -> tuple[Callable, dict[str, Any]]:
        node = self._get_node_by_method(method)

        return node.get_handler_by_path(path)
