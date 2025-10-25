# SILVANUS
The simple library for different routing with a tree-like structure

# Implementation example
Silvanus is created as a **low-level library that 
simplifies the construction** of productive, user-friendly, functional 
and customizable frameworks on top of. These can be different options 
(data buses, web, etc.), therefore, for an example of how it might look, 
there is **[silvahttp](https://github.com/Sethis/silvahttp)**.

# Paradigms:
- Each element is changeable almost beyond recognition, 
but a combination of them is possible due to common protocols 
that are well described out of the box.
- Many things are done out of the box 
(for example, the almost universal
[SimpleRouter](https://github.com/Sethis/silvanus/blob/master/silvanus/routing/simple.py)
and its two RouterIterators, which implement both the
[data queue interface with filters](https://github.com/Sethis/silvanus/blob/master/silvanus/strategy/routers/first.py)
and the 
[data bus interface with filters](https://github.com/Sethis/silvanus/blob/master/silvanus/strategy/routers/all.py)
)
- The most universal protocols, which is why it is recommended 
to write small wrappers on top of routing for frameworks.

# Usage

**First:**
```commandline
pip install silvanus
```

**Later:**

data queue interface with filters using FirstTrueRouterIterator, and
data bus interface with filters using AllTrueRouterIterator
```python
import asyncio
from dataclasses import dataclass

from silvanus.routing.simple import SimpleRouter
from silvanus.strategy.routers import FirstTrueRouterIterator, AllTrueRouterIterator
from silvanus.structures import RoutingData


@dataclass(frozen=True)
class SimpleFilter: # Our custom simple filter
    value: int
    
    async def __call__(self, data: RoutingData) -> bool:
        return data.request_data.get("value", None) == self.value
    
    
# silvanus supports all data types as a result of routing, 
# but the most useful for frameworks will be the return of functions.
def some_handler(text: str) -> str:
    return text * 2


router = SimpleRouter()

router1 = SimpleRouter([SimpleFilter(value=10)], data="wrong")

router2 = SimpleRouter([SimpleFilter(value=15), ], data=some_handler)
router3 = SimpleRouter([SimpleFilter(value=15), ], data="yes!")

router.add_routers([router1, router2, router3])

async def main():
    result = await router.route(
        data=RoutingData(
            request_data={"value": 15}
        ),
        iterator=FirstTrueRouterIterator() # get only first True result 
    )
    
    assert result("silvanus-") == "silvanus-silvanus-" # our some_handler
    
    result_2 = await router.route(
        data=RoutingData(
            request_data={"value": 15}
        ),
        iterator=AllTrueRouterIterator() # get all True result 
    )
    
    assert result_2[0](result_2[1]) == "yes!yes!" # our some_handler and text from second data 

asyncio.run(main())

```


# Examples:
  - ### [html integration example](https://github.com/Sethis/silvanus/blob/master/examples/http.py)
