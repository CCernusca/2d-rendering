
"""
Graphics module
Deals with graphical representation of geometry, including cameras
"""

import pygame as pg
import numpy as np
try:
    import scripts.geometry as geometry
except ModuleNotFoundError:
    import geometry

# Dictionary of colors for groups, indexed by group index
group_colors = {}

def color_group(group_index: int|geometry.GeoGroup, color: tuple[int, int, int, int]) -> None:
    """
    Sets the color of a group.

    Args:
        group_index (int|geometry.GeoGroup): The index of the group or the group object.
        color (tuple[int, int, int, int]): The RGBA color to set.
    """
    if group_index in geometry.groups or 0 <= group_index < len(geometry.groups):
        if type(group_index) == geometry.GeoGroup:
            group_index = geometry.groups.index(group_index)
        group_colors[group_index] = (color[0], color[1], color[2], color[3])
    else:
        raise ValueError("Invalid group index")

def uncolor_group(group_index: int|geometry.GeoGroup) -> None:
    """
    Removes the color of a group.

    Args:
        group_index (int|geometry.GeoGroup): The index of the group or the group object.
    """
    if type(group_index) == geometry.GeoGroup:
        group_index = geometry.groups.index(group_index)
    if group_index in group_colors:
        del group_colors[group_index]

def get_uncolored() -> list[int]:
    """
    Returns a list of indices of uncolored groups.

    Returns:
        list[int]: A list of indices of uncolored groups.
    """
    return [i for i in range(len(geometry.groups)) if i not in group_colors]

class Camera:
    """
    A camera, viewing a 2D scene from a specific position and angle, and rendering it to a 1D plane.

    Attributes:
        x (float): The x-coordinate of the camera.
        y (float): The y-coordinate of the camera.
        direction (float): The direction of the camera in degrees.
        field_of_view (float): The field of view of the camera in degrees.
        resolution (int): The resolution/width of the cameras viewport in pixels.
    """
    def __init__(self, x: float, y: float, direction: float, field_of_view: float, resolution: int) -> None:
        self.x = x
        self.y = y
        self.direction = direction
        self.field_of_view = field_of_view
        self.resolution = resolution

        self.viewport = pg.Surface((self.resolution, 1), pg.SRCALPHA)
    
    @property
    def beam_angles(self) -> list[float]:
        """
        Calculates the angles of beams emitted by the camera across its field of view.

        Returns:
            list[float]: A list of angles in degrees, representing the global direction of each beam, evenly spaced across the camera's field of view.
        """
        angle_per_pixel = self.field_of_view / self.resolution
        return [self.direction + angle for angle in np.arange(-self.field_of_view / 2, self.field_of_view / 2, angle_per_pixel)]
    
    def render(self, step_size: float = 1, max_distance: float = 100, *geometry_groups: int) -> list[tuple[float, float]]:
        """
        Renders the scene by simulating a 2D view from the camera's position, detecting collisions with geometry groups,
        and updating the viewport with color based on the distance to the nearest collision.

        Args:
            step_size (float, optional): The step size for ray marching. Defaults to 1.
            max_distance (float, optional): The distance a beam travels before stopping. Defaults to 100.
            geometry_groups (int, optional): Indices of geometry groups to check for collisions. If none are provided,
                                            all groups with assigned colors are considered.

        Notes:
            - The function clears and updates the camera's viewport by drawing lines representing beams emitted by the camera.
            - Each beam checks for collisions with the specified geometry groups. Detected collisions are colored in reverse, 
              so that transparency works
        """
        beam_ends = []

        if len(geometry_groups) == 0:
            geometry_groups = group_colors.keys()
        
        for beam_index, angle in enumerate(self.beam_angles):
            distance = 0
            collisions = []
            collected_alpha = 0

            # Clear pixel
            pg.draw.line(self.viewport, (0, 0, 0, 255), (beam_index, 0), (beam_index, 0))

            # Check collisions
            while distance < max_distance and collected_alpha < 255:
                for group_index in geometry_groups:
                    if group_index in group_colors and all(group_index != g for g, d in collisions):
                        group = geometry.groups[group_index]
                        if group.collides(self.x + distance * np.cos(np.deg2rad(angle)), self.y + distance * np.sin(np.deg2rad(angle))):
                            collisions.append((group_index, distance))
                            collected_alpha += group_colors[group_index][3]
                            
                distance += step_size
            
            if collisions:
                beam_ends.append((self.x + collisions[-1][1] * np.cos(np.deg2rad(angle)), self.y + collisions[-1][1] * np.sin(np.deg2rad(angle))))
            else:
                beam_ends.append((self.x + distance * np.cos(np.deg2rad(angle)), self.y + distance * np.sin(np.deg2rad(angle))))
            
            # Draw collisions
            for collision, distance in collisions[::-1]:
                # Temporary surface, required for color blending to work
                temp_surf = pg.Surface(self.viewport.get_size(), pg.SRCALPHA)
                pg.draw.line(temp_surf, 
                                (group_colors[collision][0] * (1 - distance / max_distance), 
                                 group_colors[collision][1] * (1 - distance / max_distance), 
                                 group_colors[collision][2] * (1 - distance / max_distance), 
                                 group_colors[collision][3]), 
                                (beam_index, 0), (beam_index, 0))
                self.viewport.blit(temp_surf, (0, 0))
            
        return beam_ends

if __name__ == "__main__":
    geometry.GeoGroup(5, 0, geometry.GeoCircle(0, 0, 1))
    color_group(0, (255, 0, 0, 100))
    geometry.GeoGroup(5, 5, geometry.GeoCircle(0, 0, 1))
    color_group(1, (0, 0, 255, 255))
    geometry.GeoGroup(0, 5, geometry.GeoCircle(0, 0, 1))
    color_group(2, (0, 255, 0, 255))
    geometry.GeoGroup(6, 0, geometry.GeoCircle(0, 0, 1))
    color_group(3, (255, 255, 0, 255))

    cam = Camera(0, 0, 0, 100, 100)
    cam.render()

    pg.init()
    pg.display.set_caption("Test")
    screen = pg.display.set_mode((500, 50), pg.RESIZABLE)
    clock = pg.time.Clock()
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_w:
                    cam.y -= 1
                if event.key == pg.K_s:
                    cam.y += 1
                if event.key == pg.K_a:
                    cam.x -= 1
                if event.key == pg.K_d:
                    cam.x += 1
                if event.key == pg.K_q:
                    cam.direction -= 10
                if event.key == pg.K_e:
                    cam.direction += 10
        
        cam.render(step_size=0.1, max_distance=10)
        screen.fill((0, 0, 0))
        screen.blit(pg.transform.scale(cam.viewport, screen.get_size()), (0, 0))
        pg.display.flip()

        clock.tick(60)
    
    pg.quit()
