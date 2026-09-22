from __future__ import annotations


class Vec2:
    """Generic 2D Vector

    Constructed from other `Vec2`, tuple of 2 floats or just 2 floats. Common vector operation supported:

    .. code-block:: python

        v0 = Vec2(1, 2)
        v1 = Vec2((1, 2))
        v2 = Vec2(v1)

        print(v0 + v1) # (2, 4)
        print(v2 * 3) # (3, 6)
        print(v2 / 4) # (0.25, 0.5)
    """

    def __init__(self, *args):
        if len(args) == 0:
            self.x, self.y = 0, 0
        elif len(args) == 1:
            v = args[0]
            if isinstance(v, Vec2):
                self.x, self.y = v.x, v.y
            else:
                self.x, self.y = v[0], v[1]
        else:
            self.x, self.y = args[0], args[1]

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Vec2 ({self.x}, {self.y})"

    def __sub__(self, other) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __add__(self, other) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar) -> Vec2:
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar) -> Vec2:
        return self.__mul__(scalar)

    def __neg__(self) -> Vec2:
        return Vec2(-self.x, -self.y)

    def __truediv__(self, scalar) -> Vec2:
        return Vec2(self.x / scalar, self.y / scalar)

    def __mod__(self, scalar) -> Vec2:
        return Vec2(self.x % scalar, self.y % scalar)

    def to_tuple(self):
        return (self.x, self.y)

    def __eq__(self, other):
        if other == None:
            return False
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        if other == None:
            return True
        return not (self.x == other.x and self.y == other.y)

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y

    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y

    def __gt__(self, other):
        return self.x > other.x and self.y > other.y

    def __ge__(self, other):
        return self.x >= other.x and self.y >= other.y
