

from typing import Any, Callable

from dataclasses import dataclass

from silvanus.structures import RoutingData


TypeFilterType = Callable[[str], Any]
STRING_PARAM_TYPES: dict[str, TypeFilterType] = {
    "str": str,
    "int": int,
    "float": float
}


@dataclass(slots=True, kw_only=True, frozen=True)
class TypeFilter:
    index: int

    name: str
    value_type: TypeFilterType

    async def __call__(self, data: RoutingData) -> bool:
        if data.request_data["request_len"] < self.index:
            return False

        current_string: str = data.request_data["request_path_strings"][self.index]

        try:
            result = self.value_type(current_string)

            data.filters_data[self.name] = result
            return True

        except ValueError:
            return False


@dataclass(slots=True, kw_only=True, frozen=True)
class PathFilter:
    index: int

    text: str

    async def __call__(self, data: RoutingData) -> bool:
        if data.request_data["request_len"] < self.index:
            return False

        current_string = data.request_data["request_path_strings"][self.index]

        return current_string == self.text


@dataclass(slots=True, kw_only=True, frozen=True)
class MethodFilter:
    method: str

    async def __call__(self, data: RoutingData) -> bool:
        return data.request_data["request_method"] == self.method


@dataclass(slots=True, kw_only=True, frozen=True)
class LenghtFilter:
    lenght: int

    async def __call__(self, data: RoutingData) -> bool:
        return data.request_data["request_len"] == self.lenght


def parse_path(path: str, app_data: dict[str, Any], method: str, limiter="/") -> RoutingData:
    splitted = path.split(limiter)

    return RoutingData(
        request_data={
            "request_len": len(splitted),
            "request_path_strings": splitted,
            "request_method": method
        },
        app_data=app_data
    )


def get_path_filters(
        path: str,
        param_types: dict[str, TypeFilterType],
        method: str,
        limiter="/"
) -> list[TypeFilter | PathFilter]:

    splitted = path.split(limiter)

    result = [
        MethodFilter(method=method),
        LenghtFilter(lenght=len(splitted))
    ]

    for index, param in enumerate(splitted):
        if param == "":
            continue

        if param[0] == "{" and param[-1] == "}":
            param_splitted = param.split(":")

            if len(param_splitted) > 1:
                param_name = param_splitted[0].strip()[1:]
                param_type_str = param_splitted[1].strip()[:-1]

                try:
                    param_type = STRING_PARAM_TYPES[param_type_str]

                except KeyError:
                    raise ValueError(f"undefined type after '{limiter}' limiter")

            else:
                param_name = param_splitted[0].strip()[1:-1]

                param_type = param_types.get(param_name, str)

            result.append(
                TypeFilter(
                    index=index,
                    name=param_name,
                    value_type=param_type
                )
            )
            continue

        result.append(
            PathFilter(
                index=index,
                text=param
            )
        )

    return result
