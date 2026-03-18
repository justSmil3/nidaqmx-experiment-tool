from typing import Iterable
from helper import flatten

def construct_spline(points: Iterable[float|int]):
    points_flattened = flatten(points)
    if len(points_flattened) == 0:
        raise ValueError("Trying to construct a bezier spline with no points!")
    num_unfilled = len(points_flattened) % 4
    start_pad = (num_unfilled + 1) // 2
    end_pad = (num_unfilled) // 2
    for _ in range(start_pad):
        points_flattened = [points_flattened[0]] + points_flattened
    for _ in range(end_pad):
        points_flattened += [points_flattened[-1]]

