

from typing import Optional, Any, Callable, Self
from dataclasses import dataclass, field

from silvanus.enums.separators import Separators


@dataclass(slots=True)
class Node:
    text: Optional[str] = None

    variable_name: Optional[str] = None
    variable_type: Any = None

    childs: list["Node"] = field(default_factory=list)
    handler: Optional[Callable] = None

    @classmethod
    def _get_new_node(
            cls,
            text: Optional[str] = None,
            variable_name: Optional[str] = None,
            variable_type: Any = None
    ) -> Self:
        return cls(
            text=text,
            variable_type=variable_type,
            variable_name=variable_name
        )

    @staticmethod
    def _get_second_part(path: str, node_text: str, skip: int = 0) -> str:
        return path[len(node_text) + skip:]

    def _devide_by_first_node(self, path: str, variable_types: dict[str, Any]) -> tuple["Node", str]:
        result: str = ""
        wait_close_char: bool = False

        for index, char in enumerate(path):
            if char == Separators.OPEN_CHAR and result:
                second_part = self._get_second_part(path, result)

                new_node = self._get_new_node(text=result)

                return (
                    new_node,
                    second_part
                )

            if char == Separators.OPEN_CHAR:
                wait_close_char = True
                continue

            if char == Separators.CLOSE_CHAR:
                if not wait_close_char:
                    raise ValueError("A closing symbol without an opening symbol was detected")

                variable_type = variable_types.get(result, None)

                if variable_type is None:
                    raise ValueError(f"The type of the variable '{result}' has not been declared")

                try:
                    if path[index+1] == "/":
                        skip = 3
                    else:
                        skip = 2

                except IndexError:
                    skip = 2

                second_part = self._get_second_part(path, result, skip=skip)

                new_node = self._get_new_node(
                    variable_name=result,
                    variable_type=variable_type
                )

                return (
                    new_node,
                    second_part
                )

            if char == Separators.DELIMITER:
                second_part = self._get_second_part(path, result, skip=1)

                new_node = self._get_new_node(text=result)

                return (
                    new_node,
                    second_part
                )

            result = f"{result}{char}"

        new_node = self._get_new_node(text=result)

        return (
            new_node,
            ""   # empty because this is the end
        )

    def comparison_nodes(self, node: "Node") -> bool:
        return self.text == node.text and self.variable_type is node.variable_type

    def add_child(self, path: str, variable_types: dict[str, Any], func: Callable):
        node, second_part = self._devide_by_first_node(path, variable_types)

        for child in self.childs:
            if child.comparison_nodes(node):
                if not second_part:
                    raise ValueError(f"a duplicate address was found at {path}")

                child.add_child(second_part, variable_types, func)
                return

        if not second_part:
            node.handler = func

        self.childs.append(node)

        if not second_part:
            return

        node.add_child(second_part, variable_types, func)

    def include_node(self, node: "Node"):
        for child in node.childs:
            for self_child in self.childs:
                if child.comparison_nodes(self_child):
                    self_child.include_node(child)
                    break

                self.childs.append(child)

    def sort(self):
        self.childs = sorted(self.childs)

        if self.childs:
            for child in self.childs:
                child.sort()

    def get_handler(
            self,
            path_values: list[str],
            data: Optional[dict[str, Any]] = None
    ) -> Optional[tuple[Callable, dict[str, Any]]]:

        if data is None:
            data = {}

        can_parse: bool = False

        if self.variable_type:
            try:
                var = self.variable_type(path_values[0])
                can_parse = True

                data[self.variable_name] = var

            except ValueError:
                pass

        if not (self.text == path_values[0] or can_parse):
            return None

        values = path_values[1:]

        if not values:
            return self.handler, data

        for child in self.childs:
            result = child.get_handler(values, data=data)

            if result:
                return result

        return None

    def get_handler_by_path(self, path: str) -> Optional[tuple[Callable, dict[str, Any]]]:
        values = path.split("/")

        return self.get_handler(values)

    def __lt__(self, other: "Node"):
        """
        This is used in Node.sort()
        :param other: The omparison node
        :return: true if value should be right, false if value should be left
        """

        if self.text and not other.text:
            return True

        if not self.text and other.text:
            return False

        if self.text and other.text:
            return self.text < other.text

        if self.variable_type is str:
            return False

        return True


def print_node(n: Node, back: str):
    for child in n.childs:
        text = f"{back}/{child.text or child.variable_type}"

        if not child.childs:
            text = f"{back}/{child.variable_type or child.text}"
            print(text)
            continue

        print_node(child, text)
