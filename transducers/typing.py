from typing import Union, Any, Callable, Dict, Tuple

Fn = Callable[..., Any]
Implementation = Dict[type, Fn]
Extension = Tuple[str, Fn]
Coll = Union[list, dict, set]
