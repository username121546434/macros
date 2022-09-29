from dataclasses import dataclass, field
from time import time


@dataclass(frozen=True)
class ScrollEvent:
    x: int
    y: int
    dx: int
    dy: int
    created_at: float = field(default_factory=time, init=False)
