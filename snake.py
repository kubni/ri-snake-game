class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y


class Snake() :
    def __init__(self):
        self.body = [Point(2, 2), Point(2, 3), Point(2, 4)]

    
