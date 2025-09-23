# SILVANUS
The simple library for different routing with a tree-like structure

# Paradigms:
- Each element is changeable almost beyond recognition, 
but a combination of them is possible due to common protocols 
that are well described out of the box.
- Many things are done out of the box 
(for example, the almost universal
[SimpleRouter](https://github.com/Sethis/silvanus/blob/master/silvanus/routing/simple)
and its two RouterIterators, which implement both the
[data queue interface with filters](https://github.com/Sethis/silvanus/blob/master/silvanus/strategy/routers/first)
and the 
[data bus interface with filters](https://github.com/Sethis/silvanus/blob/master/silvanus/strategy/routers/all)
)
- The most universal protocols, which is why it is recommended 
to write small wrappers on top of routing for frameworks.

# Examples:
  - ### [html integration example](https://github.com/Sethis/silvanus/blob/master/examples/http.py)
