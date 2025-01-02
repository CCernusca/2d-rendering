
"""
Utility module
Provides miscellaneous additional functionality
"""

import pygame as pg

def blit_aspect(target_surface: pg.Surface, source_surface: pg.Surface, 
                left_margin_percent: float = 0.05, top_margin_percent: float = 0.05, 
                right_margin_percent: float = 0.05, bottom_margin_percent: float = 0.05) -> None:
    """
    Blits a source_surface onto a target_surface while preserving its aspect ratio and 
    respecting margins defined as percentages of the target_surface size.

    Args:
        target_surface The surface to draw on.
        source_surface The surface to be scaled and blitted.
        left_margin_percent Margin on the left side as a percentage of target surface width.
        top_margin_percent Margin on the top side as a percentage of target surface height.
        right_margin_percent Margin on the right side as a percentage of target surface width.
        bottom_margin_percent Margin on the bottom side as a percentage of target surface height.
    """
    # Calculate the margins in pixels
    width, height = target_surface.get_size()
    left_margin = int(width * left_margin_percent)
    top_margin = int(height * top_margin_percent)
    right_margin = int(width * right_margin_percent)
    bottom_margin = int(height * bottom_margin_percent)

    # Calculate the available area after applying margins
    available_width = width - left_margin - right_margin
    available_height = height - top_margin - bottom_margin

    # Get the original dimensions of the source surface
    src_width, src_height = source_surface.get_size()

    # Calculate the scaled dimensions preserving the aspect ratio
    scale_width = available_width
    scale_height = int(src_height * (available_width / src_width))

    if scale_height > available_height:
        scale_height = available_height
        scale_width = int(src_width * (available_height / src_height))

    # Scale the source surface
    scaled_surface = pg.transform.scale(source_surface, (scale_width, scale_height))

    # Calculate the position to center the scaled surface within the available area
    x_pos = left_margin + (available_width - scale_width) // 2
    y_pos = top_margin + (available_height - scale_height) // 2

    # Blit the scaled surface onto the target surface
    target_surface.blit(scaled_surface, (x_pos, y_pos))

def screen_to_display_position(screen_position: tuple[int, int], display_size: tuple[int, int], 
                               screen_size: tuple[int, int], 
                               left_margin_percent: float = 0.05, top_margin_percent: float = 0.05, 
                               right_margin_percent: float = 0.05, bottom_margin_percent: float = 0.05) -> tuple[int, int]:
    """
    Translates a screen position into a position relative to the smaller display surface.

    :param screen_position: The position on the screen (x, y).
    :param display_size: The size of the display surface (width, height).
    :param screen_size: The size of the screen (width, height).
    :param left_margin_percent: Margin on the left side as a percentage of screen width.
    :param top_margin_percent: Margin on the top side as a percentage of screen height.
    :param right_margin_percent: Margin on the right side as a percentage of screen width.
    :param bottom_margin_percent: Margin on the bottom side as a percentage of screen height.
    :return: The translated position relative to the display surface (x, y).
    """
    # Calculate the margins in pixels
    width, height = screen_size
    left_margin = int(width * left_margin_percent)
    top_margin = int(height * top_margin_percent)
    right_margin = int(width * right_margin_percent)
    bottom_margin = int(height * bottom_margin_percent)

    # Calculate the available area after applying margins
    available_width = width - left_margin - right_margin
    available_height = height - top_margin - bottom_margin

    # Get the size of the display surface
    display_width, display_height = display_size

    # Calculate the scale factors based on the display size
    scale_width = available_width
    scale_height = int(display_height * (available_width / display_width))

    if scale_height > available_height:
        scale_height = available_height
        scale_width = int(display_width * (available_height / display_height))

    # Calculate the position of the display surface on the screen
    display_x = left_margin + (available_width - scale_width) // 2
    display_y = top_margin + (available_height - scale_height) // 2

    # Get the position on the screen relative to the display
    screen_x, screen_y = screen_position

    # Calculate the relative position within the display surface
    x_offset = screen_x - display_x
    y_offset = screen_y - display_y

    # Adjust the offset to fit the scaled display
    x_pos = int(x_offset * (display_width / scale_width))
    y_pos = int(y_offset * (display_height / scale_height))

    return x_pos, y_pos


def draw_rectangle(surface, corner1, corner2, color, width=0):
	"""
	Draws a rectangle on the given surface based on two opposite corners.

	Args:
		surface: The Pygame surface to draw on.
		corner1: A tuple (x1, y1) representing one corner of the rectangle.
		corner2: A tuple (x2, y2) representing the opposite corner of the rectangle.
		color: The color of the rectangle (e.g., (255, 0, 0) for red).
		width: The width of the rectangle's outline. Defaults to 0 (filled rectangle).
	"""
	# Calculate the top-left corner and dimensions of the rectangle
	x1, y1 = corner1
	x2, y2 = corner2
	top_left_x = min(x1, x2)
	top_left_y = min(y1, y2)
	width_rect = abs(x2 - x1)
	height_rect = abs(y2 - y1)

	# Define the rectangle
	rectangle = pg.Rect(top_left_x, top_left_y, width_rect, height_rect)

	# Draw the rectangle on the surface
	pg.draw.rect(surface, color, rectangle, width)

import pygame

def draw_circle(surface, corner1, corner2, color, width=0):
	"""
	Draws a circle on the given surface based on two opposite corners.

	Parameters:
		surface: The Pygame surface to draw on.
		corner1: A tuple (x1, y1) representing one corner of the rectangle.
		corner2: A tuple (x2, y2) representing the opposite corner of the rectangle.
		color: The color of the circle (e.g., (255, 0, 0) for red).
		width: The width of the circle's outline. Defaults to 0 (filled circle).
	"""
	# Calculate the center and diameter of the circle
	x1, y1 = corner1
	x2, y2 = corner2
	center_x = (x1 + x2) / 2
	center_y = (y1 + y2) / 2

	# Determine the smaller side length for the diameter
	diameter = min(abs(x2 - x1), abs(y2 - y1))

	# Draw the circle on the surface
	pygame.draw.circle(surface, color, (int(center_x), int(center_y)), diameter // 2, width)
