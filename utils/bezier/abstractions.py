from typing import TypedDict

class BezierPoint(TypedDict):
    point: tuple[float, float]
    leftControl: tuple[float, float]
    rightControl: tuple[float, float]
