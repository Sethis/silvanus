
import asyncio

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


@router.get("/0")
def zero_handler():
    return "0000000"


@router.get("/1")
async def async_handler():
    return "Hello from async!"


@router.get("/{foo}/{prefix}/{tree}")
def chaos_handler(prefix: str, tree: bool, foo: int):
    return prefix, tree, foo


handler, data = router.route("GET", "/me")
assert handler(**data) == "Text: 'me'"

router.sort()
# router.sort() is optional,
# but it can solve the overlapping problem
# for all router handlers when calling

handler, data = router.route("GET", "/0")
assert handler(**data) == "0000000"

handler, data = router.route("GET", "/me")
assert handler(**data) == "it's me"

handler, data = router.route("GET", "/some_text")
assert handler(**data) == "Text: 'some_text'"

handler, data = router.route("GET", "/10")
assert handler(**data) == 100

handler, data = router.route("GET", "/1")
assert asyncio.run(handler(**data)) == "Hello from async!"

handler, data = router.route("GET", "/12345/text/true")
assert handler(**data) == ("text", True, 12345)
