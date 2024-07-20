

import pytest

from silvanus import Router
from silvanus.routing import Node


def test_register_get():
    router = Router()

    @router.get("some/{data}")
    def func(data: int):
        return data

    handler_obj = router.route("GET", "/some/123")

    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result == 123


def test_nestedregister_get():
    router = Router()

    @router.get("some/{number}/{text}")
    def func(number: int, text: str):
        return number, text

    handler_obj = router.route("GET", "/some/1234/value")

    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result[0] == 1234
    assert result[1] == "value"


def test_dublicate_get():
    router = Router()

    @router.get("some/{number}/{text}")
    def func(number: int, text: str):
        return number, text

    try:
        @router.get("some/{number}/{text}")
        def func(number: int, text: str):
            return number, text

        assert False is True

    except ValueError:
        pass


def test_sort_get():
    router = Router()

    @router.get("some/{text}/{number}")
    def func(text: str, number: int):
        return text, number, 3

    @router.get("some/{number}/{text}")
    def func(number: int, text: str):
        return number, text, 1

    @router.get("some/some_text/{text}")
    def func(text: str):
        return text, 2

    @router.get("some/0/{number}")
    def func(number: int):
        return number, 4

    router.sort()

    handler_obj = router.route("GET", "/some/1234/value")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result[0] == 1234
    assert result[1] == "value"
    assert result[2] == 1

    handler_obj = router.route("GET", "/some/some_text/yes")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result[0] == "yes"
    assert result[1] == 2

    handler_obj = router.route("GET", "/some/other/123")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result[0] == "other"
    assert result[1] == 123
    assert result[2] == 3

    handler_obj = router.route("GET", "/some/0/123")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result[0] == 123
    assert result[1] == 4


def test_prefix():
    router = Router(prefix="/some")

    @router.get("/{text}/{number}")
    def func(text: str, number: int):
        return text, number, 3

    handler_obj = router.route("GET", "/some/some_text/123")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result[0] == "some_text"
    assert result[1] == 123


def test_first_separator():
    router = Router()

    @router.get("/some/{text}/{number}")
    def func(text: str, number: int):
        return text, number, 3

    handler_obj = router.route("GET", "/some/some_text/123")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result[0] == "some_text"
    assert result[1] == 123


def test_without_first_separator():
    router = Router()

    @router.get("some/{text}/{number}")
    def func(text: str, number: int):
        return text, number, 3

    handler_obj = router.route("GET", "/some/some_text/123")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result[0] == "some_text"
    assert result[1] == 123


def test_root_handler():
    router = Router()

    @router.get("/")
    def func():
        return 111

    handler_obj = router.route("GET", "/")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result == 111


def test_root_handler_prefix():
    router = Router(prefix="/")

    @router.get("")
    def func():
        return 222

    handler_obj = router.route("GET", "/")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result == 222


def test_empty_path():
    router = Router()

    try:
        @router.get("")
        def func():
            return 111

        assert True is False

    except ValueError:
        pass


def test_chaos_arguments():
    router = Router()

    @router.get("/{text}{value}{some}")
    def func(some: str, text: str, value: int):
        return some, text, value

    handler_obj = router.route("GET", "/maybe/10/cat")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result[0] == "cat"
    assert result[1] == "maybe"
    assert result[2] == 10


def test_custom_node():
    class CustomNode(Node):
        pass

    router = Router(prefix="/", node_class=CustomNode)

    @router.get("")
    def func():
        return 222

    router.sort()

    handler_obj = router.route("GET", "/")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result == 222


def test_custom_sort():
    class CustomNode(Node):
        def __lt__(self, other):
            if self.text:
                return False

            return True

    router1 = Router(node_class=CustomNode)
    router2 = Router()

    @router1.get("/me")
    def func():
        return 123

    @router1.get("/{data}")
    def func(data: str):
        return data

    router1.sort()

    @router2.get("/me")
    def func():
        return 123

    @router2.get("/{data}")
    def func(data: str):
        return data

    router2.sort()

    handler_obj = router1.route("GET", "/me")
    handler = handler_obj[0]
    result_1 = handler(**handler_obj[1])

    assert result_1 == "me"

    handler_obj = router2.route("GET", "/me")
    handler = handler_obj[0]
    result_2 = handler(**handler_obj[1])

    assert result_2 == 123

    assert result_1 != result_2


def test_different_methods():
    router = Router()

    @router.get("/me")
    def func():
        return 222

    @router.post("/me")
    def func():
        return 333

    handler_obj = router.route("GET", "/me")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result == 222

    handler_obj = router.route("POST", "/me")
    handler = handler_obj[0]
    result = handler(**handler_obj[1])

    assert result == 333


@pytest.mark.asyncio
async def test_asyncio():
    router = Router()

    @router.get("/me")
    async def func():
        return 222

    handler_obj = router.route("GET", "/me")
    handler = handler_obj[0]
    result = await handler(**handler_obj[1])

    assert result == 222