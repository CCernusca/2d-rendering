
"""
Geometry module
Deals with defining geometry and its functionality
"""

from abc import abstractmethod, ABCMeta

class GeoShape(metaclass=ABCMeta):
    """
    Basic geometry class, abstract class for concrete shapes.

    Attributes:
        x (float): The x-coordinate of the shape.
        y (float): The y-coordinate of the shape.

    Methods:
        collides(x, y): Checks whether a point collides with the shape (is inside shape).
    """
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        
    @abstractmethod
    def collides(self, x: float, y: float) -> bool:
        """
        Checks wether a point (x, y) collides with the shape (is inside shape)
        """

class GeoCircle(GeoShape):
    """
    Geometry class for circles.

    Attributes:
        x (float): The x-coordinate of the circle.
        y (float): The y-coordinate of the circle.
        r (float): The radius of the circle.

    Methods:
        collides(x, y): Checks whether a point collides with the circle (is inside circle).
    """
    def __init__(self, x: float, y: float, r: float) -> None:
        super().__init__(x, y)
        self.r = r
    
    def collides(self, x, y):
        return (x - self.x) ** 2 + (y - self.y) ** 2 <= self.r**2

class GeoRectangle(GeoShape):
    """
    Geometry class for rectangles.

    Attributes:
        x (float): The x-coordinate of the rectangle.
        y (float): The y-coordinate of the rectangle.
        w (float): The width of the rectangle.
        h (float): The height of the rectangle.

    Methods:
        collides(x, y): Checks whether a point collides with the rectangle (is inside rectangle).
    """
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        super().__init__(x, y)
        self.w = w
        self.h = h
    
    def collides(self, x, y):
        return self.x - self.w / 2 <= x <= self.x + self.w / 2 and self.y - self.h / 2 <= y <= self.y + self.h / 2

if __name__ == "__main__":
    circle = GeoCircle(0, 0, 1)
    print(circle.collides(0, 0))
    print(circle.collides(1, 0))
    print(circle.collides(1.1, 0))

    rect = GeoRectangle(0, 0, 1, 1)
    print(rect.collides(0, 0))
    print(rect.collides(0.5, 0))
    print(rect.collides(0.55, 0))
