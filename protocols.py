from functools import partial

import typing
from typing import List, Dict, Tuple, Any

Fn = typing.Callable[..., Any]


class ProtocolImplementation:
    def callable(self, o) -> Fn:
        raise NotImplementedError("Abstract method")


class InstanceMethod(ProtocolImplementation):
    def __init__(self, method_name: str):
        self._method_name = method_name

    def callable(self, o):
        return o.__getattribute__(self._method_name)


class ClassConstructor(ProtocolImplementation):
    def __init__(self):
        pass

    def callable(self, o):
        return o.__class__


class Callable(ProtocolImplementation):
    def __init__(self, callable):
        self._callable = callable

    def callable(self, o):
        return partial(self._callable, o)


__protocols: Dict[str, Dict[str, Dict[type, ProtocolImplementation]]] = {}


def protocol(name: str, methods: List[str]):
    if name not in __protocols:
        __protocols[name] = {}
    protocol = __protocols[name]
    for method in methods:
        if method not in protocol:
            protocol[method] = {}


def extend_protocol(name: str, t: type, *impls: Tuple[str, ProtocolImplementation]):
    protocol = __protocols[name]
    for (method, impl) in impls:
        __protocols[name][method][t] = impl


def get_implementation(protocol, method, o) -> typing.Callable:
    protocol_method = __protocols[protocol][method]
    # TODO support class hierarchy
    # Make sure type/base types are in preferred order
    types = [type(o)]
    impl = None
    for t in types:
        if t in protocol_method:
            impl = protocol_method[t]
    if impl is not None:
        return impl.callable(o)
    raise ValueError(
        f"Protocol {protocol}.{method} not implemented for {o} ({type(o)})"
    )
