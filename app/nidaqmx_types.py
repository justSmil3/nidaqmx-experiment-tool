from dataclasses import dataclass

@dataclass
class Sinewave():
    pass

@dataclass
class Rectwave():
    main_width: float = 0.001
    break_time: float = 0.0005
    counter_width: float = 0.0008

# not implemented yet 
class Bezierwave():
    pass
    # this only needs to contain 


SCHEMAS: dict = {
    "Sine": Sinewave,
    "Rect": Rectwave,
}
