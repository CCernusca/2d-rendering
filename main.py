
"""
Main module
Program Entry Point
"""

from scripts.geometry import GeoCircle as circle
from scripts.geometry import GeoRectangle as rect
import scripts.viewer as view

if __name__ == "__main__":
    view.add_viewer(150, 75, 0, 100, 100, 200, 10, 1)
    view.add_viewer(450, 200, 180, 200, 100, 100, 10, 1)

    view.add_geometry(325, 75, (255, 0, 0, 150), circle(0, 0, 50))
    view.add_geometry(325, 325, (0, 0, 255, 255), circle(0, 0, 50), rect(50, 0, 100, 100))
    view.add_geometry(75, 325, (0, 255, 0, 255), rect(0, 0, 100, 100))
    view.add_geometry(375, 75, (255, 255, 0, 255), circle(0, 0, 50))

    view.start()
