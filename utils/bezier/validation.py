from typing import Sequence

def direction(p1: Sequence[float], p2: Sequence[float]):
    if not validate_coordinate(p1) or not validate_coordinate(p2):
        raise ValueError("Cannot calculate distance if one or more points is not a 2d coordinate")
    x = p2[0] - p1[0]
    y = p2[1] - p1[1]
    length = sqrt(pow(x, 2) + pow(y, 2))
    return [x / length, y / length]


def validate_coordinate(p: Sequence[float]) -> bool:
    if not p:
        return False
    if not isinstance(p, Sequence):
        return False
    return len(p) == 2 and isinstance(p[0], float) and isinstance(p[1], float)

def validate_point(p: Sequence[Sequence[float]]) -> bool:
    if not p:
        return False
    if not isinstance(p, Sequence):
        return False
    return len(p) == 3 and all([validate_coordinate(x) for x in p]) and direction(p[0], p[1]) == direction(p[1], p[2])

def validate_curve(curve: Sequence[Sequence[float]]) -> bool:
    if not curve:
        return False
    if not isinstance(curve, Sequence):
        return False
    return len(curve) == 4 and all([validate_coordinate(p) for p in curve])

def validate_spline(spline: Sequence[Sequence[Sequence[float]]]) -> bool:
    if not spline:
        return False
    if not isinstance(spline, Sequence):
        return False
    return all([validate_curve(curve) for curve in spline])

