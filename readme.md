# silvanus
A simple library for URL routing with a tree-like prefix structure

# Examples:
```python
from silvanus import Router

router = Router()

@router.get("/{bar}")
def handler_too(bar: str):
    return f"Text: '{bar}'"


@router.get("/{foo}")
def handler_too(foo: int):
    return foo * 10


@router.get("/me")
def me_handler():
    return "it's me"

@router.get("/{foo}/{prefix}/{tree}")
def chaos_handler(prefix: str, tree: bool, foo: int):
    return prefix, tree, foo

router.sort()

handler, data = router.route("GET", "/me")
assert handler(**data) == "it's me"

handler, data = router.route("GET", "/some_text")
assert handler(**data) == "Text: 'some_text'"

handler, data = router.route("GET", "/10")
assert handler(**data) == 100

handler, data = router.route("GET", "/12345/text/true")
assert handler(**data) == ("text", True, 12345)
```

## Other examples of using routing: 
  - ### [full example](https://github.com/Sethis/silvanus/blob/main/examples/routing.py)
  - ### [simple asgi app example](https://github.com/Sethis/silvanus/blob/main/examples/app.py)
  - ### [examples directory](https://github.com/Sethis/silvanus/tree/main/examples)
  - ### [tests directory](https://github.com/Sethis/silvanus/tree/main/tests)