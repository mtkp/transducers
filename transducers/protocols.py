from functools import partial
import typing
from typing import Dict, Any, Iterable


from transducers.typing import Implementation, Extension


def call(name: str, impls: Implementation, o: Any, *args, **kwargs):
    # TODO support class hierarchy with type and base types in ideal order
    types = [type(o)]
    impl = None
    for t in types:
        if t in impls:
            impl = impls[t]
            break
    if callable(impl):
        return impl(o, *args, **kwargs)
    raise ValueError(
        f"Protocol method '{name}' not implemented for '{type(o).__name__}'"
    )


class Protocol:
    def __init__(self, interface: Iterable[str]):
        self.__implementations: Dict[str, Implementation] = {}
        for method in set(interface):
            self.__implementations[method] = {}

    def extend(self, t: type, *impls: Extension):
        for (method, impl) in impls:
            self.__implementations[method][t] = impl

    def __getattr__(self, name: str):
        if name in self.__implementations:
            return partial(call, name, self.__implementations[name])
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )


def protocol(*interface: str) -> Protocol:
    return Protocol(interface)
