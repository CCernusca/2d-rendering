
"""
Viewer module
Deals with user interfacing for the program
"""

import queue
import multiprocessing
import multiprocessing.queues
import pygame as pg
import numpy as np
try:
    import scripts.geometry as geometry
    import scripts.graphics as graphics
    import scripts.utils as utils
except ModuleNotFoundError:
    import geometry
    import graphics
    import utils

MOVESPEED = 10
TURNSPEED = 10
SELECTION_COLOR = (200, 200, 200, 255)

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
        step_size (int): The step size for ray marching. Defaults to 1.
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
        """
        Updates the camera's properties and renders the scene.

        Updates the camera's properties based on the viewer's properties, then renders the scene using the camera's properties and the max_distance and step_size of the viewer.
        """
        self.camera.x = self.x
        self.camera.y = self.y
        self.camera.direction = self.direction
        self.camera.field_of_view = self.field_of_view
        self.camera.resolution = self.resolution

        self.lasers = self.camera.render(max_distance=self.max_distance, step_size=self.step_size)
    
    def move(self, front_back: float, left_right: float) -> None:
        """
        Moves the viewer according to its direction and the given front_back and left_right distances.

        Args:
            front_back (float): The distance to move forward or backward.
            left_right (float): The distance to move left or right.
        """
        # Convert direction from degrees to radians
        rad = np.deg2rad(self.direction)

        # Calculate the movement in x and y
        dx = -front_back * np.cos(rad) - left_right * np.sin(rad)
        dy = -front_back * np.sin(rad) + left_right * np.cos(rad)

        # Update position
        self.x += dx
        self.y += dy
    
    def turn(self, angle: float) -> None:
        """
        Turns the viewer by the given angle in degrees.

        Args:
            angle (float): The angle in degrees to turn the viewer.
        """
        self.direction += angle

def show_geometry(surface: pg.Surface) -> None:
    """
    Shows the geometry of the scene on the given surface.

    The function renders all geometry groups in the scene with their assigned colors, and the viewers as white circles with lines representing the beams emitted by the cameras.

    Args:
        surface (pg.Surface): The surface to draw on.
    """
    surface.fill((0, 0, 0, 255))
    # Draw geometry (in reversed alpha order for transparency)
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
    
    # Draw viewers
    for viewer in viewers:
        pg.draw.circle(surface, (255, 255, 255, 255), (viewer.x, viewer.y), 5)
        for laser in viewer.lasers:
            pg.draw.line(surface, (255, 255, 255, 255), (viewer.x, viewer.y), laser, 1)

def create_viewer_window(resolution: int, control_queue: multiprocessing.Queue, display_queue: multiprocessing.Queue) -> None:
    """
    Creates a separate window for displaying the view of a single viewer.

    The function starts a new Pygame window and enters a loop where it checks for commands in the control queue, processes events, and updates the display.

    The function exits when it receives the "quit" command in the control queue, and then calls pg.quit().

    Args:
        resolution (int): The resolution/width of the display surface.
        control_queue (multiprocessing.Queue): A queue to send and receive commands from the main process.
        display_queue (multiprocessing.Queue): A queue to receive the viewer viewport from the main process.
    """
    pg.init()
    pg.display.set_caption(f"Viewer View")
    screen = pg.display.set_mode((500, 50), pg.RESIZABLE)
    clock = pg.time.Clock()
    running = True

    display = pg.Surface((resolution, 1), pg.SRCALPHA)

    while running:
        if not control_queue.empty():
            try:
                command = control_queue.get(timeout=0.1)
                if command[0] == "quit":
                    running = False
                else:
                    if command is not None:
                        control_queue.put(command)
            except queue.Empty:
                pass

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

def spawn_rectangle_from_selection(selection: list[tuple[int, int], tuple[int, int]], color: tuple[int, int, int, int] = SELECTION_COLOR) -> None:
    """
    Spawns a rectangle geometry based on the selection of two opposite corners.

    Args:
        selection (list[tuple[int, int], tuple[int, int]]): A list containing two tuples, each representing the (x, y) coordinates of a corner.
        color (tuple[int, int, int, int], optional): The RGBA color of the rectangle. Defaults to SELECTION_COLOR.

    Notes:
        - The rectangle is defined by the two corners provided in the selection.
        - The function calculates the width and height of the rectangle, and centers it around the midpoint of the selection.
    """
    width = abs(selection[1][0] - selection[0][0])
    height = abs(selection[1][1] - selection[0][1])
    x = max(selection[0][0], selection[1][0]) - width / 2
    y = max(selection[0][1], selection[1][1]) - height / 2
    add_geometry(x, y, color, geometry.GeoRectangle(0, 0, width, height))

def spawn_circle_from_selection(selection: list[tuple[int, int], tuple[int, int]], color: tuple[int, int, int, int] = SELECTION_COLOR) -> None:
    """
    Spawns a circle geometry based on the selection of two opposite corners.

    Args:
        selection (list[tuple[int, int], tuple[int, int]]): A list containing two tuples, each representing the (x, y) coordinates of a corner.
        color (tuple[int, int, int, int], optional): The RGBA color of the circle. Defaults to SELECTION_COLOR.

    Notes:
        - The circle is centered around the midpoint of the selection.
        - The radius of the circle is the minimum of the absolute difference in x and y coordinates of the two corners.
    """
    radius = min(abs(selection[1][0] - selection[0][0]), abs(selection[1][1] - selection[0][1])) / 2
    x = (selection[0][0] + selection[1][0]) / 2
    y = (selection[0][1] + selection[1][1]) / 2
    add_geometry(x, y, color, geometry.GeoCircle(0, 0, radius))

def start():
    """
    Starts the geometry window, viewer windows, and event loop.

    This function initializes the main window, creates a separate window for each viewer, and enters a loop where it processes events and updates the displays.

    The function exits when the user closes the main window, notifies all viewer windows to quit, and then calls pg.quit().

    Notes:
        - This function should be called last in the main script.
    """
    pg.init()
    pg.display.set_caption("Geometry View")
    screen = pg.display.set_mode((500, 500), pg.RESIZABLE)
    clock = pg.time.Clock()
    running = True

    display = pg.Surface((500, 500), pg.SRCALPHA)
    selection_layer = pg.Surface(display.get_size(), pg.SRCALPHA)

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

    left_mouse = False
    right_mouse = False

    left_selection = [(0, 0), (0, 0)]
    right_selection = [(0, 0), (0, 0)]

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if pg.mouse.get_pressed()[0]:
                    left_mouse = True
                if pg.mouse.get_pressed()[2]:
                    right_mouse = True
            if event.type == pg.MOUSEBUTTONUP:
                if not pg.mouse.get_pressed()[0]:
                    left_mouse = False
                    spawn_rectangle_from_selection(left_selection)
                    for viewer in viewers:
                        viewer.update()
                    show_geometry(display)
                    for viewer in viewers:
                        display_queues[viewers.index(viewer)].put(pg.surfarray.array3d(viewer.viewport))
                if not pg.mouse.get_pressed()[2]:
                    right_mouse = False
                    spawn_circle_from_selection(right_selection)
                    for viewer in viewers:
                        viewer.update()
                    show_geometry(display)
                    for viewer in viewers:
                        display_queues[viewers.index(viewer)].put(pg.surfarray.array3d(viewer.viewport))
        
        if not left_mouse:
            left_selection[0] = utils.screen_to_display_position(pg.mouse.get_pos(), display.get_size(), screen.get_size())
        left_selection[1] = utils.screen_to_display_position(pg.mouse.get_pos(), display.get_size(), screen.get_size())
        if not right_mouse:
            right_selection[0] = utils.screen_to_display_position(pg.mouse.get_pos(), display.get_size(), screen.get_size())
        right_selection[1] = utils.screen_to_display_position(pg.mouse.get_pos(), display.get_size(), screen.get_size())

        for viewer_index, control_queue in enumerate(control_queues):
            viewer = viewers[viewer_index]
            if not control_queue.empty():
                try:
                    command = control_queue.get(timeout=0.1)
                    if command[0] == "move":
                        viewer.move(*command[1])
                        viewer.update()
                    elif command[0] == "turn":
                        viewer.turn(command[1])
                        viewer.update()
                    else:
                        if command is not None:
                            control_queue.put(command)
                except queue.Empty:
                    pass
                
                # Only update displays when changes are made
                
                display_queues[viewer_index].put(pg.surfarray.array3d(viewer.viewport))

                show_geometry(display)
            
        screen.fill((50, 50, 50))
        utils.blit_aspect(screen, display)
        selection_layer.fill((0, 0, 0, 0))
        utils.draw_rectangle(selection_layer, *left_selection, SELECTION_COLOR, 2)
        utils.draw_circle(selection_layer, *right_selection, SELECTION_COLOR, 2)
        utils.blit_aspect(screen, selection_layer)
        pg.display.flip()

        clock.tick(60)
    
    for control_queue in control_queues:
        control_queue.put(("quit", None))
    pg.quit()

def add_viewer(x: float, y: float, direction: float, field_of_view: float, resolution: int, max_distance: float, step_size: int = 1) -> Viewer:
    """
    Adds a new viewer to the scene.

    Creates a Viewer instance with the specified properties and adds it to the global list of viewers.

    Args:
        x (float): The x-coordinate of the viewer's initial position.
        y (float): The y-coordinate of the viewer's initial position.
        direction (float): The initial direction of the viewer in degrees.
        field_of_view (float): The field of view of the viewer in degrees.
        resolution (int): The resolution/width of the viewer's viewport in pixels.
        max_distance (float): The maximum distance a beam travels before stopping.
        step_size (int, optional): The step size for ray marching. Defaults to 1.

    Returns:
        Viewer: The created viewer.
    """
    return Viewer(x, y, direction, field_of_view, resolution, max_distance, step_size)

def add_geometry(x: float, y: float, color: tuple[int, int, int, int], *shapes: geometry.GeoShape) -> geometry.GeoGroup:
    """
    Adds a new geometry group to the scene.

    Creates a GeoGroup with the specified shapes and assigns the given color to it.

    Args:
        x (float): The x-coordinate of the geometry group's initial position.
        y (float): The y-coordinate of the geometry group's initial position.
        color (tuple[int, int, int, int]): The RGBA color to assign to the group.
        *shapes (geometry.GeoShape): The shapes that make up the group.

    Returns:
        geometry.GeoGroup: The created geometry group.
    """
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
