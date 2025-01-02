
"""
Viewer module
Deals with user interfacing for the program
"""

import multiprocessing
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
    """
    Viewer class, wrapper for graphics.Camera, used for users to interact with the scene

    Attributes:
        x (float): The x-coordinate of the viewer.
        y (float): The y-coordinate of the viewer.
        direction (float): The direction of the viewer in degrees.
        field_of_view (float): The field of view of the viewer in degrees.
        resolution (int): The resolution/width of the viewer's viewport in pixels.
        max_distance (float): The maximum distance a beam travels before stopping.
        step_size (int): The step size for ray marching.
    """
    def __init__(self, x: float, y: float, direction: float, field_of_view: float, resolution: int, max_distance: float, step_size: int = 1) -> None:
        self.x = x
        self.y = y
        self.direction = direction
        self.field_of_view = field_of_view
        self.resolution = resolution
        self.max_distance = max_distance
        self.step_size = step_size

        self.camera = graphics.Camera(x, y, direction, field_of_view, resolution)
        # End points of the camera beams
        self.lasers = None

        self.viewport = self.camera.viewport

        viewers.append(self)
    
    def update(self) -> None:
        self.camera.x = self.x
        self.camera.y = self.y
        self.camera.direction = self.direction
        self.camera.field_of_view = self.field_of_view
        self.camera.resolution = self.resolution

        self.lasers = self.camera.render(max_distance=self.max_distance, step_size=self.step_size)
    
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
    for group_index, group_color in sorted(graphics.group_colors.items(), key=lambda x: x[1][3], reverse=True):
        # Temporary surface for transparency blending
        temp_surf = pg.Surface(surface.get_size(), pg.SRCALPHA)
        group = geometry.groups[group_index]
        for shape in group.shapes:
            if type(shape) == geometry.GeoCircle:
                pg.draw.circle(temp_surf, group_color, (shape.x, shape.y), shape.radius)
            elif type(shape) == geometry.GeoRectangle:
                pg.draw.rect(temp_surf, group_color, pg.Rect(shape.x - shape.width / 2, shape.y - shape.height / 2, shape.width, shape.height))
        surface.blit(temp_surf, (0, 0))
    for viewer in viewers:
        pg.draw.circle(surface, (255, 255, 255, 255), (viewer.x, viewer.y), 5)
        for laser in viewer.lasers:
            pg.draw.line(surface, (255, 255, 255, 255), (viewer.x, viewer.y), laser, 1)

def create_viewer_window(resolution: int, control_queue: multiprocessing.Queue, display_queue: multiprocessing.Queue) -> None:

    pg.init()
    pg.display.set_caption(f"Viewer View")
    screen = pg.display.set_mode((500, 50))
    clock = pg.time.Clock()
    running = True

    display = pg.Surface((resolution, 1), pg.SRCALPHA)

    while running:
        if not control_queue.empty():
            command = control_queue.get()
            if command[0] == "quit":
                running = False
            else:
                control_queue.put(command)

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    control_queue.put(("move", (-MOVESPEED, 0)))
                if event.key == pg.K_s:
                    control_queue.put(("move", (MOVESPEED, 0)))
                if event.key == pg.K_a:
                    control_queue.put(("move", (0, -MOVESPEED)))
                if event.key == pg.K_d:
                    control_queue.put(("move", (0, MOVESPEED)))
                if event.key == pg.K_q:
                    control_queue.put(("turn", (-TURNSPEED)))
                if event.key == pg.K_e:
                    control_queue.put(("turn", (TURNSPEED)))
        
        if not display_queue.empty():
            pg.surfarray.blit_array(display, display_queue.get())

        screen.fill((0, 0, 0))
        screen.blit(pg.transform.scale(display, screen.get_size()), (0, 0))
        pg.display.flip()

        clock.tick(60)
    
    pg.quit()

def start():

    pg.init()
    pg.display.set_caption("Geometry View")
    screen = pg.display.set_mode((500, 500))
    clock = pg.time.Clock()
    running = True

    display = pg.Surface((500, 500), pg.SRCALPHA)

    control_queues = []
    display_queues = []
    for viewer in viewers:
        control_queues.append(multiprocessing.Queue())
        display_queues.append(multiprocessing.Queue())
        multiprocessing.Process(target=create_viewer_window, args=(viewer.resolution, control_queues[-1], display_queues[-1])).start()

    for viewer in viewers:
        viewer.update()
        display_queues[viewers.index(viewer)].put(pg.surfarray.array3d(viewer.viewport))

    screen.fill((0, 0, 0))
    show_geometry(display)
    screen.blit(pg.transform.scale(display, screen.get_size()), (0, 0))
    pg.display.flip()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
        
        for viewer_index, control_queue in enumerate(control_queues):
            viewer = viewers[viewer_index]
            if not control_queue.empty():
                command = control_queue.get()
                if command[0] == "move":
                    viewer.move(*command[1])
                    viewer.update()
                elif command[0] == "turn":
                    viewer.turn(command[1])
                    viewer.update()
                else:
                    control_queue.put(command)
                
                # Only update screens when changes are made
                
                display_queues[viewer_index].put(pg.surfarray.array3d(viewer.viewport))

                screen.fill((0, 0, 0))
                show_geometry(display)
                screen.blit(pg.transform.scale(display, screen.get_size()), (0, 0))
                pg.display.flip()

        clock.tick(60)
    
    for control_queue in control_queues:
        control_queue.put(("quit", None))
    pg.quit()

def add_viewer(x: float, y: float, direction: float, field_of_view: float, resolution: int, max_distance: float, step_size: int = 1) -> None:
    return Viewer(x, y, direction, field_of_view, resolution, max_distance, step_size)

def add_geometry(x: float, y: float, color: tuple[int, int, int], *shapes: geometry.GeoShape) -> None:
    geo = geometry.GeoGroup(x, y, *shapes)
    graphics.color_group(geo, color)
    return geo

if __name__ == "__main__":
    add_viewer(150, 75, 0, 100, 100, 200)
    add_viewer(450, 200, 180, 200, 100, 100)

    add_geometry(325, 75, (255, 0, 0, 150), geometry.GeoCircle(0, 0, 50))
    add_geometry(325, 325, (0, 0, 255, 255), geometry.GeoCircle(0, 0, 50), geometry.GeoRectangle(50, 0, 100, 100))
    add_geometry(75, 325, (0, 255, 0, 255), geometry.GeoRectangle(0, 0, 100, 100))
    add_geometry(375, 75, (255, 255, 0, 255), geometry.GeoCircle(0, 0, 50))

    start()
