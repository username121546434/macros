from dataclasses import dataclass, field
from time import time


@dataclass(frozen=True)
class MousePosChange:
    x: int
    y: int
    created_at: float = field(init=False, default_factory=time)
