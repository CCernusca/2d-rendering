
"""
Geometry module
Deals with defining geometry and its functionality
"""

from abc import abstractmethod, ABCMeta
import numpy as np

shapes = []
groups = []

class GeoShape(metaclass=ABCMeta):
    """
    Basic geometry class, abstract class for concrete shapes.

    Attributes:
        x (float): The x-coordinate of the shape.
        y (float): The y-coordinate of the shape.
    """
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

        shapes.append(self)
    
    @abstractmethod
    def __repr__(self) -> str:
        """
        Returns a string representation of the shape.

        Returns:
            str: A string representation of the shape.
        """
        
    @abstractmethod
    def collides(self, x: float, y: float) -> bool:
        """
        Checks whether a point collides with the shape.

        Args:
            x (float): The x-coordinate of the point to check.
            y (float): The y-coordinate of the point to check.

        Returns:
            bool: True if the point collides with the shape, False otherwise.

        Notes:
            This method is abstract and must be implemented by concrete shape classes.
            The implementation should take into account the specific geometry and
            properties of the shape.
        """
    
    @abstractmethod
    def bounds(self) -> tuple[float, float, float, float]:
        """
        Returns the bounding box of the shape.

        Returns:
            tuple[float, float, float, float]: A tuple containing the outmost (x_min, y_min, x_max, y_max) coordinates of the bounding box.
        """

class GeoCircle(GeoShape):
    """
    Geometry class for circles.

    Attributes:
        x (float): The x-coordinate of the circle.
        y (float): The y-coordinate of the circle.
        r (float): The radius of the circle.
    """
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y)
        self.radius = radius
    
    def __repr__(self):
        return f"[{shapes.index(self)}] GeoCircle(x={self.x}, y={self.y}, radius={self.radius})"
    
    def collides(self, x, y):
        # Check if the distance between the point and the center of the circle is less than or equal to the radius
        return (x - self.x) ** 2 + (y - self.y) ** 2 <= self.radius**2

    @property
    def bounds(self):
        return self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius

class GeoRectangle(GeoShape):
    """
    Geometry class for rectangles.

    Attributes:
        x (float): The x-coordinate of the rectangle.
        y (float): The y-coordinate of the rectangle.
        w (float): The width of the rectangle.
        h (float): The height of the rectangle.
        angle (float): The rotation angle of the rectangle in degrees.
    """
    def __init__(self, x: float, y: float, width: float, height: float, angle: float = 0) -> None:
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.angle = angle
    
    def __repr__(self):
        return f"[{shapes.index(self)}] GeoRectangle(x={self.x}, y={self.y}, width={self.width}, height={self.height}, angle={self.angle})"
    
    @property
    def corners(self) -> list[tuple[float, float]]:
        """
        Returns the coordinates of all corners of the rectangle in global space.

        Returns:
            list[tuple[float, float]]: A list of (x, y) tuples representing the rectangle's corners.
        """
        # Half-dimensions for convenience
        half_w = self.width / 2
        half_h = self.height / 2

        # Define corners relative to the rectangle's center in local space
        local_corners = [
            (-half_w, -half_h),  # Bottom-left
            (half_w, -half_h),   # Bottom-right
            (half_w, half_h),    # Top-right
            (-half_w, half_h)    # Top-left
        ]

        # Angle in radians
        angle_rad = np.deg2rad(self.angle)

        # Rotate and translate corners to global space
        global_corners = []
        for lx, ly in local_corners:
            gx = self.x + (lx * np.cos(angle_rad) - ly * np.sin(angle_rad))
            gy = self.y + (lx * np.sin(angle_rad) + ly * np.cos(angle_rad))
            global_corners.append((gx, gy))

        return global_corners
    
    def collides(self, x, y) -> bool:
        # Translate point to rectangle's local space
        translated_x = x - self.x
        translated_y = y - self.y

        # Convert angle to radians
        angle_rad = np.deg2rad(-self.angle)

        # Rotate point in the opposite direction
        rotated_x = (
            translated_x * np.cos(angle_rad) - translated_y * np.sin(angle_rad)
        )
        rotated_y = (
            translated_x * np.sin(angle_rad) + translated_y * np.cos(angle_rad)
        )

        # Check if the point is within the unrotated rectangle
        half_w, half_h = self.width / 2, self.height / 2
        return -half_w <= rotated_x <= half_w and -half_h <= rotated_y <= half_h

    @property
    def bounds(self):
        return min(c[0] for c in self.corners), min(c[1] for c in self.corners), max(c[0] for c in self.corners), max(c[1] for c in self.corners)

class GeoGroup(GeoShape):
    """
    Geometry class for groups of shapes.

    Attributes:
        x (float): The x-coordinate of the group.
        y (float): The y-coordinate of the group.
        shapes (list[GeoShape]): A list of shapes that make up the group. Their positions are relative to the group's position.
    """
    def __init__(self, x: float, y: float, *shapes: GeoShape) -> None:
        self.x = x
        self.y = y
        self.shapes = shapes

        # Update shapes' positions to be relative to the group
        for shape in shapes:
            shape.x += x
            shape.y += y

        groups.append(self)
    
    def __repr__(self):
        return f"[{groups.index(self)}] GeoGroup(x={self.x}, y={self.y}, shapes={self.shapes})"
    
    def collides(self, x, y):
        for shape in self.shapes:
            if shape.collides(x, y):
                return True
        return False

    @property
    def bounds(self):
        x_min, y_min, x_max, y_max = 0, 0, 0, 0
        for shape in self.shapes:
            x_min, y_min, x_max, y_max = min(x_min, shape.bounds[0]), min(y_min, shape.bounds[1]), max(x_max, shape.bounds[2]), max(y_max, shape.bounds[3])
        return x_min, y_min, x_max, y_max

if __name__ == "__main__":
    circle = GeoCircle(0, 0, 1)
    print(circle)
    print(circle.bounds)
    print(circle.collides(0, 0))
    print(circle.collides(1, 0))
    print(circle.collides(1.1, 0))

    rect = GeoRectangle(0, 0, 1, 1, 45)
    print(rect)
    print(rect.corners)
    print(rect.bounds)
    print(rect.collides(0, 0))
    print(rect.collides(0.5, 0))
    print(rect.collides(0.55, 0))
    print(rect.collides(1, 0))

    group = GeoGroup(0, 0, circle, GeoRectangle(1, 0, 2, 2, 0))
    print(group)
    print(group.bounds)
    print(group.collides(0, 0))
    print(group.collides(1, 0))
    print(group.collides(2, 0))
    print(group.collides(2.1, 0))
    print(group.collides(-1, 0))
    print(group.collides(-1.1, 0))
    print(group.collides(-1, 1))
    print(group.collides(1, 1))
    print(group.collides(2, 1))
