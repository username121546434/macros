from pynput.mouse import Button
from dataclasses import dataclass, field
from time import time


@dataclass(frozen=True)
class MouseClick:
    x: int
    y: int
    button: Button
    pressed: bool
    created_at: float = field(default_factory=time, init=False)
