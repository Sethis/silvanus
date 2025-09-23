from typing import Any

from silvanus.structures import RoutingData


class BaseFilter:
    __current_id__ = []

    def __new__(cls, *args, **kwargs):
        cls.__current_id__.append(1)
        cls.__model_id__ = len(cls.__current_id__)
        return super().__new__(cls)

    def __hash__(self):
        return self.__model_id__

    def __eq__(self, other):
        try:
            return self.__model_id__ == other.__model_id__

        except AttributeError:
            return False


def filter_fix(func):
    if "." in func.__repr__():  # True if it's a method
        def wrapper(self, data: RoutingData) -> Any:
            return func(self, data.request_data["event"])

    else:
        def wrapper(data: RoutingData) -> Any:
            return func(data.request_data["event"])

    return wrapper
