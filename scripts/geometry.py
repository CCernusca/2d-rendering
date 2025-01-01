
"""
Geometry module
Deals with defining geometry and its functionality
"""

from abc import abstractmethod, ABCMeta
import numpy as np

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
    
    def collides(self, x, y):
        # Check if the distance between the point and the center of the circle is less than or equal to the radius
        return (x - self.x) ** 2 + (y - self.y) ** 2 <= self.radius**2

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
    
    @property
    def corners(self):
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

if __name__ == "__main__":
    circle = GeoCircle(0, 0, 1)
    print(circle.collides(0, 0))
    print(circle.collides(1, 0))
    print(circle.collides(1.1, 0))

    rect = GeoRectangle(0, 0, 1, 1, 45)
    print(rect.corners)
    print(rect.collides(0, 0))
    print(rect.collides(0.5, 0))
    print(rect.collides(0.55, 0))
    print(rect.collides(1, 0))
