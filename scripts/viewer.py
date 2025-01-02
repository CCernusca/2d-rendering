
"""
Viewer module
Deals with user interfacing for the program
"""

import pygame as pg
import numpy as np
try:
    import scripts.geometry as geometry
    import scripts.graphics as graphics
except ModuleNotFoundError:
    import geometry
    import graphics

MOVESPEED = 10
TURNSPEED = 10

viewers = []

class Viewer:
    def __init__(self, x: float, y: float, direction: float, field_of_view: float, resolution: int) -> None:
        self.x = x
        self.y = y
        self.direction = direction
        self.field_of_view = field_of_view
        self.resolution = resolution

        self.camera = graphics.Camera(x, y, direction, field_of_view, resolution)
        self.lasers = None

        self.viewport = self.camera.viewport

        viewers.append(self)
    
    def update(self) -> None:
        self.camera.x = self.x
        self.camera.y = self.y
        self.camera.direction = self.direction
        self.camera.field_of_view = self.field_of_view
        self.camera.resolution = self.resolution

        self.lasers = self.camera.render()
    
    def move(self, front_back, left_right):
        # Convert direction from degrees to radians
        rad = np.deg2rad(self.direction)

        # Calculate the movement in x and y
        dx = -front_back * np.cos(rad) - left_right * np.sin(rad)
        dy = -front_back * np.sin(rad) + left_right * np.cos(rad)

        # Update position
        self.x += dx
        self.y += dy
    
    def turn(self, angle: float) -> None:
        self.direction += angle

def show_geometry(surface: pg.Surface) -> None:
    surface.fill((0, 0, 0, 255))
    for group_index in graphics.group_colors:
        group = geometry.groups[group_index]
        for shape in group.shapes:
            if type(shape) == geometry.GeoCircle:
                pg.draw.circle(surface, graphics.group_colors[group_index], (shape.x, shape.y), shape.radius)
            elif type(shape) == geometry.GeoRectangle:
                pg.draw.rect(surface, graphics.group_colors[group_index], pg.Rect(shape.x - shape.width / 2, shape.y - shape.height / 2, shape.width, shape.height))
    for viewer in viewers:
        pg.draw.circle(surface, (255, 255, 255, 255), (viewer.x, viewer.y), 5)
        for laser in viewer.lasers:
            pg.draw.line(surface, (255, 255, 255, 255), (viewer.x, viewer.y), laser, 1)

def start():

    pg.init()
    pg.display.set_caption("Geometry View")
    screen = pg.display.set_mode((500, 500), pg.RESIZABLE)
    clock = pg.time.Clock()
    running = True

    display = pg.Surface((500, 500), pg.SRCALPHA)

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_w:
                    for viewer in viewers:
                        viewer.move(-MOVESPEED, 0)
                if event.key == pg.K_s:
                    for viewer in viewers:
                        viewer.move(MOVESPEED, 0)
                if event.key == pg.K_a:
                    for viewer in viewers:
                        viewer.move(0, -MOVESPEED)
                if event.key == pg.K_d:
                    for viewer in viewers:
                        viewer.move(0, MOVESPEED)
                if event.key == pg.K_q:
                    for viewer in viewers:
                        viewer.turn(-TURNSPEED)
                if event.key == pg.K_e:
                    for viewer in viewers:
                        viewer.turn(TURNSPEED)
        
        for viewer in viewers:
            viewer.update()

        screen.fill((0, 0, 0))
        show_geometry(display)
        screen.blit(pg.transform.scale(display, screen.get_size()), (0, 0))
        pg.display.flip()

        clock.tick(60)
    
    pg.quit()

if __name__ == "__main__":
    Viewer(0, 0, 0, 100, 100)
    
    geometry.GeoGroup(250, 0, geometry.GeoCircle(0, 0, 50))
    graphics.color_group(0, (255, 0, 0, 100))
    geometry.GeoGroup(250, 250, geometry.GeoCircle(0, 0, 50))
    graphics.color_group(1, (0, 0, 255, 255))
    geometry.GeoGroup(0, 250, geometry.GeoRectangle(0, 0, 100, 100))
    graphics.color_group(2, (0, 255, 0, 255))
    geometry.GeoGroup(300, 0, geometry.GeoCircle(0, 0, 50))
    graphics.color_group(3, (255, 255, 0, 255))

    start()
