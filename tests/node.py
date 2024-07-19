

from functools import partial

import pytest

from plastic.routing.node import Node


def some_fn(value: int):
    return value


def test_adding():
    node = Node(text="")

    node.add_child("value", {}, partial(some_fn, value=1))
    assert node.childs[0].text == "value"


def test_adding_child():
    node = Node(text="")

    node.add_child("value/other/some", {}, partial(some_fn, value=1))
    assert node.childs[0].text == "value"
    assert node.childs[0].childs[0].text == "other"
    assert node.childs[0].childs[0].childs[0].text == "some"


def test_adding_variable():
    node = Node(text="")

    node.add_child("value/{some}/some", {"some": int}, partial(some_fn, value=1))

    assert node.childs[0].childs[0].text is None
    assert node.childs[0].childs[0].variable_type is int


def test_adding_two_variable():
    node = Node(text="")

    node.add_child("value/{some}/some", {"some": int}, partial(some_fn, value=1))
    node.add_child("value/{some}/some", {"some": str}, partial(some_fn, value=1))

    assert node.childs[0].childs[1].text is None
    assert node.childs[0].childs[1].variable_type is str


def test_sorting():
    node = Node(text="")

    node.add_child("value/{some}", {"some": int}, partial(some_fn, value=1))
    node.add_child("value/me", {"some": str}, partial(some_fn, value=1))

    node.sort()

    assert node.childs[0].childs[0].text == "me"
    assert node.childs[0].childs[0].variable_type is None

    assert node.childs[0].childs[1].text is None
    assert node.childs[0].childs[1].variable_type is int


def test_getting():
    node = Node(text="")

    node.add_child("value/some", {"some": int}, partial(some_fn, value=11))

    handler = node.get_handler_by_path("/value/some")

    assert handler[0]() == 11


def test_getting_var():
    node = Node(text="")

    node.add_child("value/some", {"some": int}, partial(some_fn, value=11))
    node.add_child("{some}/data", {"some": int}, partial(some_fn, value=22))

    handler = node.get_handler_by_path("/111/data")

    assert handler[0]() == 22


def test_getting_var_without_sorted():
    node = Node(text="")

    node.add_child("{some}/data", {"some": str}, partial(some_fn, value=22))
    node.add_child("value/data", {"some": int}, partial(some_fn, value=33))

    handler = node.get_handler_by_path("/value/data")

    assert handler[0]() == 22


def test_getting_var_with_sorted():
    node = Node(text="")

    node.add_child("{some}/data", {"some": str}, partial(some_fn, value=22))
    node.add_child("value/data", {"some": int}, partial(some_fn, value=33))

    node.sort()

    handler = node.get_handler_by_path("/value/data")

    assert handler[0]() == 33


def test_sorting_different_types():
    node = Node(text="")

    node.add_child("some/{data}", {"data": str}, partial(some_fn, value=11))
    node.add_child("some/{data}", {"data": int}, partial(some_fn, value=22))
    node.add_child("some/data", {}, partial(some_fn, value=33))

    node.sort()

    handler = node.get_handler_by_path("/some/data")
    assert handler[0]() == 33

    handler = node.get_handler_by_path("/some/123")
    assert handler[0]() == 22

    handler = node.get_handler_by_path("/some/values")
    assert handler[0]() == 11


def test_dublicate():
    node = Node(text="")

    node.add_child("some/{data}", {"data": str}, partial(some_fn, value=11))

    try:
        node.add_child("some/{data}", {"data": str}, partial(some_fn, value=22))
        assert False is True

    except ValueError:
        pass

    handler = node.get_handler_by_path("/some/data")
    assert handler[0]() == 11


def test_include_test():
    node1 = Node(text="")
    node2 = Node(text="")

    node1.add_child("some/{data}", {"data": str}, partial(some_fn, value=11))
    node2.add_child("some/other", {"data": str}, partial(some_fn, value=22))
    node2.add_child("some/other/value", {"data": str}, partial(some_fn, value=33))
    node2.add_child("some/{other}/value/data", {"other": int}, partial(some_fn, value=44))

    node1.include_node(node2)
    node1.sort()

    handler = node1.get_handler_by_path("/some/other")
    assert handler[0]()== 22
    handler = node1.get_handler_by_path("/some/others")
    assert handler[0]() == 11

    handler = node1.get_handler_by_path("/some/other/value")
    assert handler[0]()== 33
    handler = node1.get_handler_by_path("/some/1234/value/data")
    assert handler[0]() == 44


def test_nested_data():
    node = Node(text="")

    node.add_child(
        "some/{data}/{other}/{value}", {"data": int, "other": str, "value": int},
        partial(some_fn, value=55)
    )

    handler = node.get_handler_by_path("/some/123/asdas/2312")
    assert handler[0]() == 55