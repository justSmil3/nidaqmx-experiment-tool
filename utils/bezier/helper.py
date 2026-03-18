from typing import Any, Iterable


def flatten(x: Any):
    if not isinstance(x, Iterable):
        return [x]
    result = []
    for v in x:
        result += flatten(v)
    return result


