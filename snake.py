# TODO: WIP
from PySide6.QtCore import QObject, Signal


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y


class Snake(QObject):

    signal_snake_moved = Signal(list)
    signal_snake_moved_noargs = Signal()

    def __init__(self):
        super().__init__()
        self.body = [Point(2, 2), Point(2, 3), Point(2, 4)]
        self.fitness = -1  # NOTE: Placeholder

    def emit_snake_moved(self):
        self.signal_snake_moved.emit(self.body)

    def placeholder_change_body(self):
        self.body = [Point(2, 2), Point(2, 3), Point(3, 2)]
