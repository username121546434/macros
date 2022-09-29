from __future__ import annotations
from time import time


class MouseMovementMeta(type):
    def __call__(cls: type[MouseMovement], x, y):
        for movement in cls._alive:
            if time() - movement.created_at < 1:
                movement.add_move(x, y)
                return movement
        obj = cls.__new__(cls, x, y)
        cls.__init__(obj, x, y)
        cls._alive.append(obj)
        return obj

class MouseMovement(metaclass=MouseMovementMeta):
    _alive: list[MouseMovement] = []
    def __init__(self, x: int, y: int) -> None:
        self.created_at = time()
        self.x_path: list[int] = []
        self.y_path: list[int] = []
        self.path: list[tuple[int, int, float]] = []

        self.add_move(x, y)

    def add_move(self, x: int, y: int):
        if x in self.x_path and y in self.y_path:
            return

        self.x_path.append(x)
        self.y_path.append(y)
        self.path.append((x, y, time()))
    
    def __repr__(self) -> str:
        return str(self.path)

