

import pytest

from plastic import Router


def test_register_get():
    router = Router()

    @router.get("some/{data}")
    def func(data: int):
        return data

    handler_obj = router.route("GET", "/some/123")

    handler = handler_obj[0]
    result = handler(*handler_obj[1])

    assert result == 123


def test_nestedregister_get():
    router = Router()

    @router.get("some/{number}/{text}")
    def func(number: int, text: str):
        return number, text

    handler_obj = router.route("GET", "/some/1234/value")

    handler = handler_obj[0]
    result = handler(*handler_obj[1])

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
    result = handler(*handler_obj[1])

    assert result[0] == 1234
    assert result[1] == "value"
    assert result[2] == 1

    handler_obj = router.route("GET", "/some/some_text/yes")
    handler = handler_obj[0]
    result = handler(*handler_obj[1])

    assert result[0] == "yes"
    assert result[1] == 2

    handler_obj = router.route("GET", "/some/other/123")
    handler = handler_obj[0]
    result = handler(*handler_obj[1])

    assert result[0] == "other"
    assert result[1] == 123
    assert result[2] == 3

    handler_obj = router.route("GET", "/some/0/123")
    handler = handler_obj[0]
    result = handler(*handler_obj[1])

    assert result[0] == 123
    assert result[1] == 4
